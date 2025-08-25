import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from get_cafe_data import generate_fake_cafe, generate_fake_review, generate_fake_user
from app import db, Cafe, app, User, Review

def generate_cafe_users():
    return [generate_fake_user() for _ in range(5)]

def generate_cafe_data():
    return [generate_fake_cafe() for _ in range(10)]

def generate_cafe_reviews():
    cafes = Cafe.query.all()
    users = User.query.all()
    if not cafes:
        print("No cafes found in the database.")
        return

    if not users:
        print("No users found in the database.")
        return

    reviews = []
    for cafe in cafes:
        for _ in range(random.randint(1, 5)):  # Each cafe can have 1 to 5 reviews
            user = random.choice(users)
            reviews.append(generate_fake_review(cafe.id, user.id))
    return reviews

def populate_db():
    with app.app_context():
        users = generate_cafe_users()
        db.session.bulk_insert_mappings(User, users)

        cafes = generate_cafe_data()
        db.session.bulk_insert_mappings(Cafe, cafes)

        reviews = generate_cafe_reviews()
        db.session.bulk_insert_mappings(Review, reviews)

        db.session.commit()

def delete_all_cafes():
    with app.app_context():
        Cafe.query.delete()
        db.session.commit()

if __name__ == "__main__":
    populate_db()
