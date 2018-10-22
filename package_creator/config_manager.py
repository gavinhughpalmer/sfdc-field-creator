import json


class ConfigManager(object):
    class __Singleton(object):
        def __init__(self, config_location):
            print "Reading config file at " + config_location
            with open(config_location, "r") as config_file:
                self.config = json.load(config_file)

    __instance = {}

    def __init__(self, config_location):
        if config_location not in ConfigManager.__instance:
            ConfigManager.__instance[config_location] = ConfigManager.__Singleton(config_location)

        self.config = ConfigManager.__instance[config_location].config

    def __getattr__(self, name):
        return self.config[name]
