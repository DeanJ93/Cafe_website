import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from get_cafe_data import generate_fake_cafe
from app import db, Cafe, app

def populate_db():
    with app.app_context():
        cafes = [generate_fake_cafe() for _ in range(10)]
        db.session.bulk_insert_mappings(Cafe, cafes)
        db.session.commit()

def delete_all_cafes():
    with app.app_context():
        Cafe.query.delete()
        db.session.commit()

if __name__ == "__main__":
    delete_all_cafes()
    populate_db()