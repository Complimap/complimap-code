from flask import Flask, request, send_from_directory, abort
from json import dumps as jsonify
from server.database import session as db
from server.database import init_db
from server import models

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


@app.route("/get_nodes/<int:pathid>")
def get_nodes(pathid):
    path = models.Path.query.get(pathid)
    if not path:
        abort(404)
    hops = [{'lng': n.longitude, 'lat': n.lattitude,
             'time_created': str(n.time_created), 'person': n.owner}
            for n in path.hops]
    return jsonify(hops)


@app.route("/new_node", methods=['POST'])
def new_node():
    code = request.form.get('code')
    name = request.form.get('name', default="UNK")
    lat = request.form.get('lat', default=0)
    lng = request.form.get('lng', default=0)

    path = models.add_node(name, lat, lng, code)
    if not path:
        return abort(403)
    db.add(path)
    db.commit()

    return repr(path.next_code)


@app.before_first_request
def flask_init_db():
    init_db()


@app.teardown_request
def session_clear(exception=None):
    db.remove()
    if exception and db.is_active:
        db.rollback()
