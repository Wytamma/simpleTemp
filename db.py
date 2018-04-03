from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from pony import orm
from datetime import datetime

app = Flask(__name__)
api = Api(app)

db = orm.Database()

class Probe(db.Entity):
    probe_id = orm.PrimaryKey(str)
    records = orm.Set('Record')

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
    Probe(probe_id=probe_id)

parser = reqparse.RequestParser()
parser.add_argument('probe_id')

class ProbeLists(Resource):
    def get(self):
        """list of probes"""
        with orm.db_session:
            return {
                'data':[probe.probe_id for probe in Probe.select()] 
            }

    def post(self):
        """add probe"""
        args = parser.parse_args()
        probe_id = args['probe_id']
        with orm.db_session:
            probe = Probe.get(probe_id=probe_id)
        if probe:
            return {'message': 'Probe already exists!'}
        create_probe(probe_id)
        return {'message': 'Probe created!'}


class Records(Resource):
    def get(self, probe_id):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int)
        parser.add_argument('offset', type=int)
        args = parser.parse_args()
        with orm.db_session:
            records = Probe.get(
                    probe_id=probe_id
                    ).records.order_by(orm.desc(Record.time))[args['offset']:args['limit']]
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
    app.run(host='0.0.0.0', threaded=True, debug=True, port=5000)