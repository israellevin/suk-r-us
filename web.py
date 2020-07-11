'suk-R-us Web server.'
import os

import flask
import redis

APP = flask.Flask('suk-r-us')
APP.config['SECRET_KEY'] = os.urandom(24)
REDIS = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


@APP.route("/health", methods=['GET'])
def contact_handler():
    'Say hi.'
    REDIS.lpush('hi', '1')
    return 'hi'


@APP.route('/')
@APP.route('/<path:path>', methods=['GET', 'POST'])
def catch_all_handler(path='index.html'):
    'All undefined endpoints try to serve from the root directory.'
    for directory in '.':
        if os.path.isfile(os.path.join(directory, path)):
            return flask.send_from_directory(directory, path)
    return flask.jsonify({'status': 403, 'error': "Forbidden path: {}".format(path)}), 403
