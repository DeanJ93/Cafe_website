from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, logout_user, login_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import secrets
from datetime import datetime, timedelta, timezone
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = dotenv.get_key(".env", "db_uri")  # Update with your database URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = dotenv.get_key(".env", "secret_key")  # Change this to a secure secret key

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Update with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = dotenv.get_key(".env", "mail_username")  # Update with your email
app.config['MAIL_PASSWORD'] = dotenv.get_key(".env", "mail_password")  # Update with your email password/app password

mail = Mail(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    map_url = db.Column(db.String(200), nullable=False)
    img_url = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(20), nullable=False)
    has_sockets = db.Column(db.Boolean, default=False)
    has_toilet = db.Column(db.Boolean, default=False)
    has_wifi = db.Column(db.Boolean, default=False)
    can_take_calls = db.Column(db.Boolean, default=False)
    seats = db.Column(db.String(10))
    coffee_price = db.Column(db.String, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    time_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_updated = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    reset_code = db.Column(db.String(8))
    reset_code_expires = db.Column(db.DateTime)
    time_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_updated = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
        
    def set_reset_code(self):
        self.reset_code = ''.join(secrets.choice('0123456789') for _ in range(6))
        self.reset_code_expires = datetime.now(timezone.utc) + timedelta(minutes=15)
        return self.reset_code

    def verify_reset_code(self, code):
        if not self.reset_code or not self.reset_code_expires:
            return False
        if datetime.now(timezone.utc) > (self.reset_code_expires.replace(tzinfo=timezone.utc) if self.reset_code_expires else datetime.now(timezone.utc)):
            return False
        return self.reset_code == code
    
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    cafes = Cafe.query.all()
    return render_template("index.html", cafes=cafes)

@app.route("/<int:cafe_id>")
def get_cafe(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    return render_template("cafe.html", cafe=cafe)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_cafe():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("has_sockets")),
            has_toilet=bool(request.form.get("has_toilet")),
            has_wifi=bool(request.form.get("has_wifi")),
            can_take_calls=bool(request.form.get("can_take_calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
            created_by=current_user.id,
            time_created=datetime.now(timezone.utc)
        )
        db.session.add(new_cafe)
        db.session.commit()
        flash("Cafe added successfully!")
        return redirect(url_for("index"))
    return render_template("cafe-form.html")

@app.route("/edit/<int:cafe_id>", methods=["GET", "POST"])
@login_required
def edit_cafe(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    if cafe.created_by != current_user.id:
        flash("You can only edit cafes that you've added.")
        return redirect(url_for("index"))
    
    if request.method == "POST":
        cafe.name = request.form.get("name")
        cafe.map_url = request.form.get("map_url")
        cafe.img_url = request.form.get("img_url")
        cafe.location = request.form.get("location")
        cafe.has_sockets = bool(request.form.get("has_sockets"))
        cafe.has_toilet = bool(request.form.get("has_toilet"))
        cafe.has_wifi = bool(request.form.get("has_wifi"))
        cafe.can_take_calls = bool(request.form.get("can_take_calls"))
        cafe.seats = request.form.get("seats")
        cafe.coffee_price = request.form.get("coffee_price")
        cafe.last_updated = datetime.now(timezone.utc)

        db.session.commit()
        flash("Cafe updated successfully!")
        return redirect(url_for("get_cafe", cafe_id=cafe.id))
    
    return render_template("cafe-form.html", cafe=cafe)

@app.route("/delete/<int:cafe_id>", methods=["GET","POST"])
@login_required
def delete_cafe(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    if cafe.created_by != current_user.id:
        flash("You can only delete cafes that you've added.")
        return redirect(url_for("index"))
    
    db.session.delete(cafe)
    db.session.commit()
    flash("Cafe deleted successfully!")
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").lower()
        email = request.form.get("email").lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return render_template("register.html")
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.")
            return render_template("register.html")

        new_user = User(username=username, email=email, time_created=datetime.now(timezone.utc))
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username').lower()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        
        if user:
            reset_code = user.set_reset_code()
            
            # Send email with reset code
            msg = Message('Password Reset Request',
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[user.email])
            msg.body = f'''To reset your password, use this verification code: {reset_code}

If you did not make this request, please ignore this email.
'''
            mail.send(msg)
            
            db.session.commit()
            flash('Check your email for the instructions to reset your password')
            return redirect(url_for('reset_password_verify', token=secrets.token_urlsafe(32)))
        
        flash('Email address not found')
        return redirect(url_for('reset_password_request'))
    
    return render_template('reset-password.html', token=None)

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password_verify(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == "POST":
        code = request.form.get("code")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        if len(new_password) < 6:
            flash("Password must be at least 6 characters long.")
            return redirect(url_for('reset_password_verify', token=token))
        
        if new_password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('reset_password_verify', token=token))
        
        user = User.query.filter_by(reset_code=code).first()
        if user and user.verify_reset_code(code):
            user.set_password(new_password)
            user.reset_code = None
            user.reset_code_expires = None
            user.last_updated = datetime.now(timezone.utc)
            db.session.commit()
            flash('Your password has been reset.')
            return redirect(url_for('login'))
        
        flash('Invalid or expired reset code')
        return redirect(url_for('reset_password_verify', token=token))
    
    return render_template('reset-password.html', token=token)

@app.route("/my-account", methods=["GET", "POST"])
@login_required
def my_account():
    if request.method == "POST":
        email = request.form.get("email")
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Verify current password
        if not current_user.check_password(current_password):
            flash("Current password is incorrect.")
            return redirect(url_for("my_account"))

        # Check if email already exists
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash("Email address already in use.")
            return redirect(url_for("my_account"))

        # Update email
        current_user.email = email

        # Update password if provided
        if new_password:
            if len(new_password) < 6:
                flash("New password must be at least 6 characters long.")
                return redirect(url_for("my_account"))
            
            if new_password != confirm_password:
                flash("New passwords do not match.")
                return redirect(url_for("my_account"))
            
            current_user.set_password(new_password)

        current_user.last_updated = datetime.now(timezone.utc)
        db.session.commit()
        flash("Account updated successfully.")
        return redirect(url_for("my_account"))

    return render_template("my-account.html")

if __name__ == "__main__":
    app.run(debug=True)