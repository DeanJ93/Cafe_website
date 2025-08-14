from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, logout_user, login_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db-cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
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

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class UserCafes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafe.id'))

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
            created_by=current_user.id
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
        username = request.form.get("username")
        email = request.form.get("email")
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

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
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

if __name__ == "__main__":
    app.run(debug=True)