from paths import update_working_directory
from influx import Influx
from ui import UI
from path_getter import resource_path

def main() :
    default_config_file = resource_path('config/client.config')  # Default config file

    influx = Influx()
    influx.initialize(default_config_file)

    ui = UI()
    ui.set_db_callback(influx.influxdb_read)
    ui.show_window()


if __name__ == '__main__':
    update_working_directory()
    main()
