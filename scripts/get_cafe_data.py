from faker import Faker
import requests
import random

fake = Faker()

def generate_fake_cafe():
    return {
        "name": fake.company() + " Cafe",
        "location": fake.address(),
        "img_url": requests.get("https://coffee.alexflipnote.dev/random.json").json().get("file", ""),
        "map_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2228.7700361566544!2d144.9611403005041!3d-37.814480554718834!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x6ad646b5d2ba4df7%3A0x4045675218ccd90!2sMelbourne%20VIC!5e0!3m2!1sen!2sau!4v1755944191303!5m2!1sen!2sau",
        "has_sockets": random.choice([True, False]),
        "has_wifi": random.choice([True, False]),
        "can_take_calls": random.choice([True, False]),
        "seats": random.randint(10, 30),
        "coffee_price": round(random.uniform(2.0, 5.0), 2),
        "created_by": 1,
        "time_created": fake.date_time_this_year()
    }

def generate_fake_review(cafe_id: int, user_id: int):
    return {
        "rating": random.randint(1, 5),
        "content": fake.sentence(nb_words=15),
        "cafe_id": cafe_id,
        "user_id": user_id
    }

def generate_fake_user():
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(length=8)
    }
