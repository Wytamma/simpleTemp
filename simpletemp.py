import argparse
from pony import orm
from datetime import datetime
from ds18b20 import all_probes
from time import sleep

# Build argument parser, this allows you to parse comands from the cli
parser = argparse.ArgumentParser(description='Simple script that reads all connected DS18B20 temperature probes and saves to a local DB.')
parser.add_argument('-i', '--interval', help='Sampling interval (seconds)', type=int, default=600)
args = vars(parser.parse_args())
# default vars
samping_interval = args['interval']

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

def run():
    for p in all_probes():
        probe = Probe.get(probe_id=p.probe_id)
        if not probe:
            create_probe(p.probe_id)
        temp = p.read_temperature()
        if temp is None:
            print('Could not read probe:', p)
            continue
        print(p, temp)
        add_temp_rec(temp, datetime.now(), p.probe_id)

if __name__ == "main":
    while True:
        run()
        sleep(samping_interval)