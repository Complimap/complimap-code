from flask import Flask, request, send_from_directory, make_response
from json import dumps as jsonify
from datetime import datetime as dt
from datetime import timedelta
from server.database import session as db
from server.database import init_db
from server.models import Event

import sqlalchemy as sa

app = Flask(__name__)

counters = ['sm', 'lo', 'la']


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static',
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return send_from_directory('static', 'index.html')


@app.before_first_request
def flask_init_db():
    init_db()


@app.teardown_request
def session_clear(exception=None):
    db.remove()
    if exception and db.is_active:
        db.rollback()
