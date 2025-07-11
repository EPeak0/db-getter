from paths import update_working_directory
from src.cloudio.influx import Influx
from src.cloudio.ui import UI

def main() :
    default_config_file = '../../config/client.config'  # Default config file

    influx = Influx()
    influx.initialize(default_config_file)

    ui = UI()

    while True:
        pass

if __name__ == '__main__':
    update_working_directory()
    main()
