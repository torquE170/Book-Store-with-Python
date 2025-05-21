import os
import sys
from configparser import ConfigParser


class UserSettings:

    at_cli = 0  # toggle to 1 to use getpass when at cli for password entry
    use_sqlite3 = 0  # toggle to 1 to use a local sqlite3 file as a database

    @staticmethod
    def set_config():
        try:
            user_settings = UserSettings.read_config("config.ini", "USER-SETTINGS")
            UserSettings.at_cli = int(user_settings["at_cli"])
            UserSettings.use_sqlite3 = int(user_settings["use_sqlite3"])
        except ValueError:
            print("Invalid config file")
            exit()
        except KeyError:
            print("Missing key in config file")
            exit()
        except FileNotFoundError:
            print("Missing config file")
            exit()

    @staticmethod
    def read_config(file_name, settings):
        # read the file
        config_object = ConfigParser()
        if not os.path.exists(file_name):
            raise FileNotFoundError
        config_object.read(file_name)

        # get config options
        values = config_object[settings]
        return values

    @staticmethod
    def read_menu_option(prompt):
        while True:
            try:
                number = int(input(prompt))
                return number
            except ValueError:
                return -1

    @staticmethod
    def clear():
        if "win" in sys.platform:
            os.system("cls")
        elif "linux" in sys.platform:
            os.system("clear")