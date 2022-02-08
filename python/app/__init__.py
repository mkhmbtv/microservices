from flask import Flask, abort, jsonify, request
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from .config import Configuration
from .models import db, Rating


app = Flask(__name__)
app.config.from_object(Configuration)
db.init_app(app)
Migrate(app, db)


@app.before_request
def before_request():
    if request.remote_addr != "127.0.0.1":
        return abort(403)


@app.route('/')
def test():
    return 'Hello from test route'


@app.route('/ratings/<int:book_id>')
def get_book_ratings(book_id):
    ratings = Rating.query \
        .filter(Rating.book_id == book_id).all()

    if len(ratings) == 0:
        return {"Error": 'No ratings for this book yet.'}, 404

    total = sum([rating.value for rating in ratings])
    average_value = round(total / len(ratings), 2)
    values = [{'value': rating.value} for rating in ratings]

    return jsonify({"average": average_value,
                    "ratings": values})


@app.route('/ratings/<int:book_id>', methods=['POST'])
def rate_book(book_id):
    if not request.args:
        return {'Error': 'Bad data'}, 400
    if 'value' not in request.args or 'email' not in request.args:
        return {'Error': 'Misssing arguments'}, 400

    try:
        new_rating = {'book_id': int(book_id),
                      'value': int(request.args['value']),
                      'email': request.args['email']}
        rating = Rating(**new_rating)
        db.session.add(rating)
        db.session.commit()
        return jsonify({'id': rating.id, **new_rating})
    except IntegrityError as error:
        print(error)
        return {'Error': 'Each user can only submit one rating per book.'}, 400
