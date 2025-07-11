import sys
import os
from datetime import datetime
from pytz import timezone
from influxdb import InfluxDBClient
import csv
from collections import defaultdict

from paths import update_working_directory  # Must be included before any other local packages/modules
# Add local modules here
update_working_directory()

config = None or dict


def parse_config_file(config_file):
    global config

    from configobj import ConfigObj  # pip install configobj

    config = None

#   path_config_file = path_helpers.prettify(config_file)
    path_config_file = config_file

    if path_config_file and os.path.isfile(path_config_file):
        config = ConfigObj(path_config_file)

    if config:
        # Check if most important certs parameters are present
        assert 'cloudio-db' in config, 'Missing group \'cloudio-db\' in config file!'

        assert 'host' in config['cloudio-db'], 'Missing \'host\' parameter in cloudio-db group!'
        assert 'port' in config['cloudio-db'], 'Missing \'port\' parameter in cloudio-db group!'
        assert 'username' in config['cloudio-db'], 'Missing \'username\' parameter in cloudio-db group!'
        assert 'password' in config['cloudio-db'], 'Missing \'password\' parameter in cloudio-db group!'
        assert 'database-name' in config['cloudio-db'], 'Missing \'database-name\' parameter in cloudio-db group!'

    else:
        sys.exit(u'Error reading config file')

    return config


def get_data(topic, start, stop):
    from pytz import utc

    # Connexion InfluxDB
    host = config['cloudio-db']['host']
    port = config['cloudio-db']['port']
    user = config['cloudio-db']['username']
    password = config['cloudio-db']['password']
    dbname = config['cloudio-db']['database-name']
    client_influx = InfluxDBClient(host, port, user, password, dbname)

    # Conversion datetime
    tz = timezone('Europe/Amsterdam')
    date_start = tz.localize(datetime.strptime(start, '%d-%m-%Y %H:%M:%S')).astimezone(utc)
    date_stop = tz.localize(datetime.strptime(stop, '%d-%m-%Y %H:%M:%S')).astimezone(utc)

    # Requête avec précision à la seconde
    query = (
        f'SELECT value FROM "{topic}" '
        f'WHERE time >= \'{date_start.isoformat()}\' '
        f'AND time <= \'{date_stop.isoformat()}\''
    )

    print("Query -->", query)

    # Exécution
    results = client_influx.query(query)
    return list(results.get_points())


def influxdb_read(start_date, stop_date):
    import argparse

    global config

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='Cloud.IO InfluxDB Read')
    parser.add_argument('-c', '--config', help='Application configuration file')
    # Parse arguments given from the command line
    args = parser.parse_args()

    default_config_file = '../../config/client.config'  # Default config file

    # Check if configuration file were given via application argument
    config_file = args.config or default_config_file
    config = parse_config_file(config_file)

    print('Starting data collection')

    data_retrieved = {}

    topics = [
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.base-settings.attributes.production-rate',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.measures.attributes.psu-voltage',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.measures.attributes.stack-current',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.stack-informations.attributes.h-2-flow-rate',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.measures.attributes.electrolyte-temperature',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.measures.attributes.downstream-temperature',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.measures.attributes.inner-hydrogen-pressure',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.measures.attributes.outer-hydrogen-pressure',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.measures.attributes.water-inlet-pressure',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.dryer-informations.attributes.dryer-tt-00',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.dryer-informations.attributes.dryer-tt-01',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.dryer-informations.attributs.dryer-pt-00',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.dryer-informations.attributs.dryer-pt-01',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.water-tank-control.attributes.level',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.water-tank-control.attributes.conductivity',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.water-tank-control.attributes.inlet-temperature',
        'dcbus_hydrogen_storage_system_intermediate.nodes.electrolysis_enapter.objects.water-tank-control.attributes.tank-temperature'
    ]

    for topic in topics:
        data_retrieved[topic] = get_data(topic=topic,
                                         start=start_date,
                                         stop=stop_date)

    # TODO: Process and analyse data
    print('# TODO: Process and analyse data')
    print(data_retrieved)
    write_to_csv(data_retrieved, 'data.csv')
    print('Finished')


def write_to_csv(data: dict, filename: str):
    # Préparer les données sous forme : {time: {topic: value, ...}, ...}
    time_series = defaultdict(dict)

    for topic, entries in data.items():
        for entry in entries:
            timestamp = entry["time"]
            value = entry["value"]
            time_series[timestamp][topic] = value

    # Obtenir tous les timestamps triés
    sorted_times = sorted(time_series.keys())

    # Obtenir tous les topics (en-têtes de colonnes)
    topics = list(data.keys())

    # Écrire dans le fichier CSV
    with open(filename, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)

        # Ligne d'en-tête
        header = ["time"] + topics
        writer.writerow(header)

        # Écrire les lignes avec les valeurs, vides si absentes
        for timestamp in sorted_times:
            row = [timestamp]
            for topic in topics:
                row.append(time_series[timestamp].get(topic, ""))
            writer.writerow(row)

    print(f"CSV écrit avec succès dans : {filename}")

def main() :
    start_date = '03-07-2025 13:51:30'
    stop_date = '03-07-2025 14:56:00'
    influxdb_read(start_date, stop_date)

if __name__ == '__main__':
    main()
