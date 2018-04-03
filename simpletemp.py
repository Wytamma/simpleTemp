from ds18b20 import all_probes
import argparse
from datetime import datetime
from time import sleep
import requests

# Build argument parser, this allows you to parse comands from the cli
parser = argparse.ArgumentParser(description='Simple script that reads all connected DS18B20 temperature probes and saves to a local DB.')
parser.add_argument('-i', '--interval', help='Sampling interval (seconds)', type=int, default=600)
parser.add_argument('-d', '--database', help='IP address of database server', type=str, default='0.0.0.0:5000')


args = vars(parser.parse_args())
# default vars

url = 'http://{}/'.format(args['database'])
samping_interval = args['interval']

local_probes_list = [] 

def run():
    for p in all_probes():
        if p.probe_id not in local_probes_list:
            try:
                r = requests.post(url + 'probes', data = {'probe_id':p.probe_id})
                print(p, r.json()['message'])
                local_probes_list.append(p.probe_id)
            except requests.exceptions.ConnectionError:
                print('ConnectionError: could not connect to host.')
        temp = p.read_temperature()
        if temp is None:
            print('Could not read probe:', p)
            continue
        print(datetime.now().isoformat(), p, temp)
        try:
            r = requests.post(url + 'records/' + p.probe_id, data = {'temperature':temp, 'time':datetime.now().isoformat()})
            if r.status_code != requests.codes.ok:
                print(p, 'Database request failed.')
        except requests.exceptions.ConnectionError:
            print('ConnectionError: could not connect to host.')

if __name__ == '__main__':
    while True:
        run()
        sleep(samping_interval)