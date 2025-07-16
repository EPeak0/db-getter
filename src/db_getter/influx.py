import os
from datetime import datetime
from pytz import timezone, utc
from influxdb import InfluxDBClient
from configobj import ConfigObj

class Influx:
    def __init__(self):
        self.config = None
        self.client_influx = None
        self.initialized = False

    # PUBLIC
    def initialize(self, config_path):
        # Check if the config file exists
        if config_path and os.path.isfile(config_path):
            self.config = ConfigObj(config_path)
        else:
            raise 'no influx config file'

        # Check if the config file is correct
        if self.config:
            # Check if the most important certs parameters are present
            assert 'cloudio-db' in self.config, 'Missing group \'cloudio-db\' in config file!'
            assert 'host' in self.config['cloudio-db'], 'Missing \'host\' parameter in cloudio-db group!'
            assert 'port' in self.config['cloudio-db'], 'Missing \'port\' parameter in cloudio-db group!'
            assert 'username' in self.config['cloudio-db'], 'Missing \'username\' parameter in cloudio-db group!'
            assert 'password' in self.config['cloudio-db'], 'Missing \'password\' parameter in cloudio-db group!'
            assert 'database-name' in self.config[
                'cloudio-db'], 'Missing \'database-name\' parameter in cloudio-db group!'

        else:
            raise 'error in influx config file'

        # Connection InfluxDB
        host = self.config['cloudio-db']['host']
        port = self.config['cloudio-db']['port']
        user = self.config['cloudio-db']['username']
        password = self.config['cloudio-db']['password']
        dbname = self.config['cloudio-db']['database-name']
        self.client_influx = InfluxDBClient(host, port, user, password, dbname)

        self.initialized = True

    # PUBLIC
    def influxdb_read(self, start_date, stop_date, topics):
        if not self.initialized:
            raise 'initialize() must be called before use'

        data_retrieved = {}

        for topic in topics:
            data_retrieved[topic] = self.get_data(topic=topic,
                                             start=start_date,
                                             stop=stop_date)

        return data_retrieved

    # PRIVATE
    def get_data(self, topic, start, stop):
        tz = timezone('Europe/Amsterdam')
        date_start = tz.localize(datetime.strptime(start, '%d-%m-%Y %H:%M:%S')).astimezone(utc)
        date_stop = tz.localize(datetime.strptime(stop, '%d-%m-%Y %H:%M:%S')).astimezone(utc)

        # Request
        query = (
            f'SELECT value FROM "{topic}" '
            f'WHERE time >= \'{date_start.isoformat()}\' '
            f'AND time <= \'{date_stop.isoformat()}\''
        )

        # Exécution
        results = self.client_influx.query(query)
        return list(results.get_points())
