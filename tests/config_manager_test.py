import unittest2 as unittest
import shutil
import os
import ConfigManager

temp_dir = "./tmp/"
config_filepath = temp_dir + "temp.json"
value = "testValue"


class ConfigManagerTest(unittest.TestCase):
    def setUp(self):
        # create config file to use in the tests
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        with open(config_filepath, "w+") as config_file:
            config_file.write("{\"test_element\": \"" + value + "\"}")  # TODO use format

    def test_read(self):
        config = ConfigManager(config_filepath)
        self.assertEquals(value, config.test_element, "The element should have been returned from the config manager")

    def test_read_invalid_json(self):
        pass

    def tearDown(self):
        shutil.rmtree(temp_dir)
