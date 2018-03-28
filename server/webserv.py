from flask import Flask, request, send_from_directory, abort
from json import dumps as jsonify
from server.database import session as db
from server.database import init_db
from server import models
from email.utils import formatdate

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static',
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/paths/")
def get_paths():
    paths = models.Path.query.all()
    if not paths:
        abort(404)
    paths = [{'id': p.id, 'time_created': str(p.time_created),
              'time_updated': str(p.time_updated), 'message': p.message}
            for p in paths]
    return jsonify(paths)

@app.route("/paths/all")
@app.route("/paths/all/nodes")
def all_paths():
    paths = models.Path.query.all()
    if not paths:
        abort(404)
    paths = {p.id: {
              'nodes': [{'lng': n.longitude, 'lat': n.lattitude,
                'time_created': str(n.time_created), 'person': n.owner}
                for n in p.hops],
              'time_created': str(p.time_created),
              'time_updated': str(p.time_updated), 'message': p.message}
            for p in paths}
    return jsonify(paths)

@app.route("/paths/<int:pathid>/nodes")
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
    data = request.get_json()
    if not data:
        return abort(400)

    if 'code' in data:
        code = data['code']
    else:
        return abort(400)

    if 'name' in data:
        name = data['name']
    else:
        name = 'UNK'

    if 'lat' in data:
        lat  = data['lat']
    else:
        lat = 0

    if 'lng' in data:
        lng  = data['lng']
    else:
        lng = 0

    path = models.add_node(name, lat, lng, code)
    if not path:
        return abort(403)
    db.add(path)
    db.commit()

    return jsonify({'message':path.message,'next_code':path.next_code})

@app.before_first_request
def flask_init_db():
    init_db()

@app.teardown_request
def session_clear(exception=None):
    db.remove()
    if exception and db.is_active:
        db.rollback()
