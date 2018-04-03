import argparse
from datetime import datetime
from time import sleep

# Build argument parser, this allows you to parse comands from the cli
parser = argparse.ArgumentParser(description='Simple script that reads all connected DS18B20 temperature probes and saves to a local DB.')
parser.add_argument('-i', '--interval', help='Sampling interval (seconds)', type=int, default=600)
parser.add_argument('-d', '--database', help='IP address of database server', type=str, default='0.0.0.0:5000')


args = vars(parser.parse_args())
# default vars

url = 'http://{}/'.format(args['database'])
samping_interval = args['interval']

def run():
    r = requests.get(url+'records/example1?limit=1')
    print(r.json())

if __name__ == "main":
    while True:
        run()
        sleep(samping_interval)