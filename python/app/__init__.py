from flask import Flask, jsonify
from flask_migrate import Migrate
from .config import Configuration
from .models import db, Rating


app = Flask(__name__)
app.config.from_object(Configuration)
db.init_app(app)
Migrate(app, db)


@app.route('/')
def test():
    return 'Hello from test route'


@app.route('/ratings/<int:book_id>')
def get_book_ratings(book_id):
    ratings = Rating.query \
        .filter(Rating.book_id == book_id).all()

    if len(ratings) == 0:
        return {"error": 'No ratings for this book yet.'}, 404

    total = sum([rating.value for rating in ratings])
    average_value = round(total / len(ratings), 2)
    values = [{'value': rating.value} for rating in ratings]

    return jsonify({"average": average_value,
                    "ratings": values})
