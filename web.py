'suk-R-us Web server.'
import os

import flask
import redis

APP = flask.Flask('suk-r-us')
APP.config['SECRET_KEY'] = os.urandom(24)
REDIS = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


@APP.route("/create_game", methods=['POST'])
def create_game():
    'Create a game and join it.'
    game_id = flask.request.get_json()['game_id']
    if REDIS.sadd('games', game_id) != 1:
        return flask.jsonify(dict(success=False, error=f"game {game_id} already exists")), 400
    return flask.jsonify(dict(success=True))


@APP.route("/open_games", methods=['GET'])
def open_games():
    'Get a list of all open games.'
    return flask.jsonify(dict(games=[game.decode('utf-8') for game in REDIS.smembers('games')]))


@APP.route('/')
@APP.route('/<path:path>', methods=['GET', 'POST'])
def catch_all_handler(path='index.html'):
    'All undefined endpoints try to serve from the root directory.'
    for directory in '.':
        if os.path.isfile(os.path.join(directory, path)):
            return flask.send_from_directory(directory, path)
    return flask.jsonify({'status': 403, 'error': "Forbidden path: {}".format(path)}), 403
