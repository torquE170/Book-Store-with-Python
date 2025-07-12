import os
import sys
from configparser import ConfigParser


class UserSettings:

    at_cli = 0  # toggle to 1 to use getpass when at cli for password entry
    use_sqlite3 = 0  # toggle to 1 to use a local sqlite3 file as a database
    user_library_name = ""  # set name of the in use book library
    loans_table_name = ""  # set name of the in use loans table

    @staticmethod
    def set_config():
        """
        Reads config.ini file for relevant user settings and loads them into the program.
        Executing stop if the config file isn't formated or has invalid values
        If the file is missing a default config file will be created
        """
        try:
            user_settings = UserSettings.read_config("config.ini", "USER-SETTINGS")
            UserSettings.at_cli = int(user_settings["at_cli"])
            UserSettings.use_sqlite3 = int(user_settings["use_sqlite3"])
            user_settings = UserSettings.read_config("config.ini", "USER-LIBRARY")
            UserSettings.user_library_name = user_settings["library_table"]
            UserSettings.loans_table_name = user_settings["loans_table"]
        except ValueError:
            print("Invalid config file")
            exit()
        except KeyError:
            print("Missing key in config file")
            exit()
        except FileNotFoundError:
            print("Missing config file")
            print()
            UserSettings.init_cfg_file()
            print("Default config file created, edit it with relevant information")
            print("Exiting")
            print()
            exit()

    @staticmethod
    def read_config(file_name, settings):
        """
        Uses ConfigParser to read a file
        :param file_name:
        :param settings:
        :return: Section object with key 'settings' from the whole ConfigParser object
        """
        # read the file
        config_object = ConfigParser()
        if not os.path.exists(file_name):
            raise FileNotFoundError
        config_object.read(file_name)

        # get config options
        values = config_object[settings]
        return values

    @staticmethod
    def edit_config(file_name, settings, key, value):
        """
        Change a certain value in the config file, using ConfigParser
        :param file_name:
        :param settings:
        :param key:
        :param value:
        """
        # read the file
        config_object = ConfigParser()
        if not os.path.exists(file_name):
            raise FileNotFoundError
        config_object.read(file_name)

        # edit the value
        config_object.set(settings, key, value)

        # write the file
        with open(file_name, "w") as conf:
            config_object.write(conf)

    @staticmethod
    def init_cfg_file():
        """
        Creates a config file with default values, and highest compatibility, user needs to change them in
        order to use a standalone mysql server or run app at terminal with getpass() for password entering
        """
        # Get the configparser object
        config_object = ConfigParser()

        # Config data
        config_object["USER-SETTINGS"] = {
            "at_cli": "0",
            "use_sqlite3": "1"
        }
        config_object["USER-LIBRARY"] = {
            "library_table": "BookStore",
            "loans_table": "Loans"
        }
        config_object["DB-CONNECTION"] = {
            "host": "mysql-server-ip",
            "port": "3306",
            "user": "python-user",
            "password": "python-password",
            "database": "python"
        }

        # Write the above sections to config.ini file
        with open('config.ini', 'w') as conf:
            config_object.write(conf)

    @staticmethod
    def read_menu_option(prompt):
        """
        Makes sure user enters an int
        :param prompt:
        :return: the number user entered or -1 if user entered anything else
        """
        while True:
            try:
                number = int(input(prompt))
                return number
            except ValueError:
                return -1

    @staticmethod
    def clear():
        """
        calls clear for windows or linux
        """
        if "win" in sys.platform:
            os.system("cls")
        elif "linux" in sys.platform:
            os.system("clear")