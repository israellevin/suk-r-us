'suk-R-us Web server.'
import functools
import os
import logging
import traceback

import flask
import redis

APP = flask.Flask('suk-r-us')
APP.config['SECRET_KEY'] = os.urandom(24)
REDIS = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))

# Help pylint understand the flask logger object.
LOGGER = logging.getLogger() and APP.logger


def optional_arg_decorator(decorator):
    'A decorator for decorators than can accept optional arguments.'
    @functools.wraps(decorator)
    def wrapped_decorator(*args, **kwargs):
        'A wrapper to return a filled up function in case arguments are given.'
        if len(args) == 1 and not kwargs and callable(args[0]):
            return decorator(args[0])
        return lambda decoratee: decorator(decoratee, *args, **kwargs)
    return wrapped_decorator


# Since this is a decorator the handler argument will never be None, it is
# defined as such only to comply with python's syntactic sugar.
@optional_arg_decorator
def call(handler=None, required_fields=None):
    """
    A decorator to handle API calls: it extracts arguments, validates and
    fixes them and passes them to the handler, dealing with exceptions and
    returning a processed, valid response.
    """
    if required_fields is None:
        required_fields = set()

    @functools.wraps(handler)
    def _call(*_, **__):
        args = flask.request.get_json() or {}
        missing_fields = required_fields - set(args.keys())
        if missing_fields:
            return flask.jsonify(dict(
                success=False, status=400, error=f"request does not contain field(s): {', '.join(missing_fields)}"
            )), 400

        # pylint: disable=broad-except
        # If anything fails, we want to catch it here.
        try:
            response = handler(**args)
        except Exception:
            LOGGER.exception(f"unknown server exception {flask.request.url}({args})")
            response = dict(
                success=False, status=500, error='unknown error', stack=traceback.format_exc().split('\n'))
        # pylint: enable=broad-except

        if not isinstance(response, dict):
            response = dict(success=False, status=500, error='invalid response from handler')
        elif 'success' not in response:
            response['success'] = True

        if 'error' in response:
            LOGGER.error(f"error {flask.request.url}({args}) - {response['error']}")

        try:
            return flask.jsonify(response), response.get('status', 200)
        except TypeError:
            return flask.jsonify(dict(
                success=False, status=500, error='non jsonable response from handler'
            )), 500

    return _call


@APP.route("/create_game", methods=['POST'])
@call({'player_id', 'game_id'})
def create_game(player_id, game_id):
    'Create a game and join it.'
    if REDIS.sadd('games', game_id) != 1:
        return dict(success=False, status=400, error=f"game {game_id} already exists")
    REDIS.rpush(f"game-{game_id}-participants", player_id)
    return dict()


@APP.route("/open_games", methods=['GET'])
@call()
def open_games():
    'Get a list of all open games.'
    return dict(games=[game.decode('utf-8') for game in REDIS.smembers('games')])


@APP.route('/')
@APP.route('/<path:path>', methods=['GET', 'POST'])
def catch_all_handler(path='index.html'):
    'All undefined endpoints try to serve from the root directory.'
    for directory in '.':
        if os.path.isfile(os.path.join(directory, path)):
            return flask.send_from_directory(directory, path)
    return flask.jsonify(dict(succes=False, status=404, error=f"path {path} not found")), 404
