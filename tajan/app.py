from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys


app = Flask(__name__)

client = MongoClient('mongodb://test:test@3.34.179.28', 27017)
db = client.dbjungle

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


app.json = CustomJSONProvider(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/list', methods=['GET'])
def show_movies():
    sortMode = request.args.get('sortMode')
    movies = list(db.movies.find({'trashed': False}))

    if sortMode == 'likes':
        sorted_movies = sorted(movies, key=lambda x: x['likes'], reverse=True)
    elif sortMode == 'viewers':
        sorted_movies = sorted(movies, key=lambda x: x['viewers'], reverse=True)
    elif sortMode == 'date':
        sorted_movies = sorted(movies, key=lambda x: (x['open_year'], x['open_month'], x['open_day']), reverse=True)
    else :
        return jsonify({'result' : 'failure'})
    return jsonify({'result': 'success', 'movies_list': sorted_movies})


@app.route('/api/trash_list', methods=['GET'])
def show_trash() :
    sortMode = request.args.get('sortMode')
    movies = list(db.movies.find({'trashed' : True}))

    if sortMode == 'likes':
        sorted_movies = sorted(movies, key=lambda x: x['likes'], reverse=True)
    elif sortMode == 'viewers':
        sorted_movies = sorted(movies, key=lambda x: x['viewers'], reverse=True)
    elif sortMode == 'date':
        sorted_movies = sorted(movies, key=lambda x: (x['open_year'], x['open_month'], x['open_day']), reverse=True)
    else :
        return jsonify({'result' : 'failure'})
    return jsonify({'result': 'success', 'movies_list': sorted_movies})


@app.route('/api/like', methods=['POST'])
def like_movie():
    movieId = ObjectId(request.form['movieId'])

    movie = db.movies.find_one({'_id' : movieId})
    new_likes = movie['likes'] + 1
    result = db.movies.update_one({'_id' : movieId}, {'$set': {'likes': new_likes}})

    if result.modified_count == 1:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})


@app.route('/api/goTrash', methods=['POST'])
def goTrash() :
    movieId = ObjectId(request.form['movieId'])
    result = db.movies.update_one({'_id' : movieId}, {'$set' : {'trashed' : True}})

    if result.modified_count == 1 :
        return jsonify({'result' : 'success'})
    else :
        return jsonify({'result' : 'failure'})


@app.route('/api/noTrash', methods=['POST'])
def noTrash() :
    movieId = ObjectId(request.form['movieId'])
    result = db.movies.update_one({'_id' : movieId}, {'$set' : {'trashed' : False}})

    if result.modified_count == 1 :
        return jsonify({'result' : 'success'})
    else :
        return jsonify({'result' : 'failure'})


@app.route('/api/deathTrash', methods=['POST'])
def deathTrash() :
    movieId = ObjectId(request.form['movieId'])
    result = db.movies.delete_one({'_id' : movieId})

    if result.deleted_count == 1 :
        return jsonify({'result' : 'success'})
    else :
        return jsonify({'result' : 'failure'})


if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
