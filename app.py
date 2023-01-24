# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# шаг 2
# Напишите сериализацию модели `Movie`.
# Установите Flask-RESTX, создайте CBV для обработки GET-запроса.
# - `/movies` — возвращает список всех фильмов, разделенный по страницам;
# - `/movies/<id>` — возвращает подробную информацию о фильме.


class MovieSchema(Schema):
    """модель для сериализации фильмов"""
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    """модель для сериализации режиссеров"""
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    """модель для сериализации жанров"""
    id = fields.Int()
    name = fields.Str()


# взяли с библиотеки flask_restx класс Api и теперь можем создавать namespace
api = Api(app)
# создаем namespace
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


# Создаем экземпляр класса
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True) # many для обращения к нескольким объектам
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


# здесь регистрируем класс (CBV)
@movie_ns.route('/')
# наследуем класс от класса Resource
class MoviesView(Resource):
    def get(self):
        movie_query = db.session.query(Movie)
        director_id = request.args.get('director_id')
        if director_id is not None:
            movie_query = movie_query.filter(Movie.director_id == director_id)

        genre_id = request.args.get('genre_id')
        if genre_id is not None:
            movie_query = movie_query.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(movie_query.all()), 200

    def post(self):
        req_json = request.json
        new_movies = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movies)
        return "", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid:int):
        try:
            movie = db.session.query(Movie).get(uid)
            return movie_schema.dump(movie), 200
        except Exception:
            return "", 404


    def put(self, uid:int):
        try:
            movie = Movie.query.get(uid)
            req_json = request.json
            # movie.id = req_json.get('id') не нужно
            movie.title = req_json.get('title')
            movie.description = req_json.get('description')
            movie.trailer = req_json.get('trailer')
            movie.year = req_json.get('year')
            movie.rating = req_json.get('rating')
            movie.genre_id = req_json.get('genre_id')
            movie.director_id = req_json.get('director_id')
            db.session.add(movie)
            db.session.commit()
            return "", 204
        except Exception:
            return "", 400


    def delete(self, uid:int):
        movie = Movie.query.get(uid)
        db.session.delete(movie)
        db.session.commit()
        return "", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_director = Director.query.all()
        return directors_schema.dump(all_director), 200


    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "", 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid:int):
        try:
            director = Director.query.get(uid)
            return director_schema.dump(director), 200
        except Exception:
            return "", 404


    def put(self, uid:int):
        try:
            director = Director.query.get(uid)
            req_json = request.json
            # director.id = req_json.get('id')
            director.name = req_json.get('name')
            db.session.add(director)
            db.session.commit()
            return "", 204
        except Exception:
            return "", 404


    def delete(self, uid:int):
        director = Director.query.get(uid)
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genre = Genre.query.all()
        return genres_schema.dump(all_genre), 200


    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid:int):
        try:
            genre = Genre.query.get(uid)
            return genre_schema.dump(genre), 200
        except Exception:
            return "", 404


    def put(self, uid:int):
        try:
            genre = Genre.query.get(uid)
            req_json = request.json
            genre.name = req_json.get('name')
            db.session.add(genre)
            db.session.commit()
            return "", 204
        except Exception:
            return "", 404


    def delete(self, uid:int):
        genre = Genre.query.get(uid)
        db.session.delete(genre)
        db.session.commit()
        return "", 204




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9000, debug=True)
