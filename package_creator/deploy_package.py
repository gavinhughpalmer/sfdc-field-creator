from config_manager import ConfigManager
from field_creator import PackageCreator
import shutil
from sfdclib import SfdcSession
from sfdclib import SfdcMetadataApi
import time

# TODO put this into  class


class DeployPackage(object):
    def __init__(self, config_path):
        self.config = ConfigManager(config_path)
        self.enviroment = ConfigManager(self.config.enviroment_location)
        self.package_path = self.config.temp_dir + "/src"
        self.package_zip = self.config.temp_dir + "/package"

    def perform_deployment(self):
        self.__generate_package()
        self.__zip_package()
        self.__deploy_package()
        # self.__remove_tmp_dir()

    def __generate_package(self):
        object_creator = PackageCreator(
            self.enviroment,
            self.config
        )
        object_creator.write_package(self.package_path)
        print "Package Generated!"

    def __zip_package(self):
        shutil.make_archive(self.package_zip, "zip", self.package_path)
        self.package_zip += ".zip"

    def __deploy_package(self):
        session = self.__salesforce_login()
        metadata_api = SfdcMetadataApi(session)
        print "Deploying Generated Package..."
        checkonly = self.config.checkonly if hasattr(self.config, "checkonly") else True
        deployment_id, state = metadata_api.deploy(self.package_zip, {"checkonly": checkonly})
        self.__poll_results(metadata_api, deployment_id, state)

    def __salesforce_login(self):
        session = SfdcSession(
            self.enviroment.username,
            self.enviroment.password,
            self.enviroment.token,
            self.enviroment.is_sandbox,
            self.enviroment.api_version
        )
        print "Logging in as " + self.enviroment.username
        # should error handle
        session.login()
        return session

    def __poll_results(self, metadata_api, deployment_id, state):
        deployment_results = None
        while state == "InProgress" or state == "Queued" or state == "Pending":
            # move into a logger functionality
            print state
            deployment_results = metadata_api.check_deploy_status(deployment_id)
            state = deployment_results[0]
            time.sleep(self.config.poll_wait)

        print state
        for index, error in enumerate(deployment_results[2]["errors"]):
            print "  %d.) %s" % (index + 1, error)

    def __remove_tmp_dir(self):
        shutil.rmtree(self.config.temp_dir)
