from configparser import ConfigParser

# Get the configparser object
config_object = ConfigParser()

# Config data
config_object["USER-SETTINGS"] = {
    "at_cli": "1"
}
config_object["DB-CONNECTION"] = {
    "host" : "192.168.188.87",
    "port" : "33006",
    "user" : "python-user",
    "password" : "python-password",
    "database" : "python"
}

# Write the above sections to config.ini file
with open('config.ini', 'w') as conf:
    config_object.write(conf)
