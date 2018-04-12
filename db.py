from flask import Flask, request, abort, make_response, jsonify, send_file, render_template
from flask_restful import Resource, Api, reqparse
from pony import orm
from datetime import datetime
import os
from flask_cors import CORS
from flask_csv import send_csv

app = Flask(__name__,
            static_folder = "./webapp-simpletemp/dist",
            template_folder = "./webapp-simpletemp/dist",
            static_url_path='')
            
CORS(app)
api = Api(app)

db = orm.Database()

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/csv')
def csv():
    print("loading data...")
    with orm.db_session:
        return send_csv([   
            {'probe_id': record.probe.probe_id, 
            'name': record.probe.name,
            'temperature': record.temperature,
            'time': record.time,
            'id': record.id
            } for record in Record.select()],
        "temperature_data.csv", ["id", "probe_id", "name", "temperature", "time"], cache_timeout=0)

@app.route('/database')
def database():
    return send_file('temperature_db.sqlite')
    
class Probe(db.Entity):
    probe_id = orm.PrimaryKey(str)
    name = orm.Optional(str)
    records = orm.Set('Record')
    max = orm.Required(float)
    min = orm.Required(float)

class Record(db.Entity):
    temperature = orm.Required(float)
    time = orm.Required(datetime)
    probe = orm.Required(Probe)

db.bind(provider='sqlite', filename='temperature_db.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

@orm.db_session
def add_temp_rec(temperature, time, probe_id):
    Record(temperature=temperature, 
           time=time, 
           probe=Probe[probe_id])

@orm.db_session
def create_probe(probe_id):
    Probe(probe_id=probe_id, name=probe_id, max=30, min=20)

@orm.db_session
def get_probe_or_404(probe_id):
    probe = Probe.get(probe_id=probe_id)
    if not probe:
        abort(make_response(jsonify(message="Probe not found."), 404))
    return probe

class ProbeLists(Resource):
    def get(self):
        """list of probes"""
        with orm.db_session:
            return {
                'data':[
                    {'probe_id':probe.probe_id, 
                    'name':probe.name,
                    'max':probe.max,
                    'min':probe.min,
                    } for probe in Probe.select()] 
                }

    def post(self):
        """add probe"""
        parser = reqparse.RequestParser()
        parser.add_argument('probe_id')
        args = parser.parse_args()
        probe_id = args['probe_id']
        with orm.db_session:
            probe = Probe.get(probe_id=probe_id)
            if probe:
                return {'message': 'Probe already exists!'}
        create_probe(probe_id)
        return {'message': 'Probe created!'}

    def put(self):
        """edit probe"""
        print(request)
        parser = reqparse.RequestParser()
        parser.add_argument('probe_id')
        parser.add_argument('name')
        parser.add_argument('max')
        parser.add_argument('min')
        args = parser.parse_args()
        probe_id = args['probe_id']
        with orm.db_session:
            probe = get_probe_or_404(probe_id)
            probe.name = args['name'] or probe.name
            probe.max = args['max'] or probe.max
            probe.min = args['min'] or probe.min
            return {'message': 'Probe updated!'}


class Records(Resource):
    def get(self, probe_id):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int)
        parser.add_argument('offset', type=int)
        args = parser.parse_args()
        with orm.db_session:
            probe = get_probe_or_404(probe_id)
            records = probe.records.order_by(orm.desc(Record.time))[args['offset']:args['limit']]
            return {'data': [{
                'temperature':r.temperature, 
                'time':r.time.isoformat(),
                'probe_id': probe_id,
                'id': r.id} for r in records]
                }

    def post(self, probe_id):
        """Add records"""
        parser = reqparse.RequestParser()
        parser.add_argument('temperature', required=True, type=float)
        parser.add_argument('time', required=True, type=str)
        args = parser.parse_args()
        time = datetime.strptime(args['time'], '%Y-%m-%dT%H:%M:%S.%f')
        add_temp_rec(args['temperature'], time, probe_id)
        return {'message': 'Record created!'}

api.add_resource(ProbeLists, '/probes')
api.add_resource(Records, '/records/<probe_id>')

if __name__ == '__main__':
    f = os.popen("""ifconfig wlan0 | awk '/inet addr/ {gsub("addr:", "", $2); print $2}'""")
    ip=f.read()
    port = 5000
    print(' * Access database locally on:', ip.strip() + ':' + str(5000))
    app.run(host='0.0.0.0', threaded=True, port=port)