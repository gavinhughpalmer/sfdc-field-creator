from spreadsheet_reader import read_spreadsheet
from xml_writer import Xml
from metadata_builder import ObjectMetadataBuilder
from row_translator import SalesforceField

# TODO could include something similar for mass profile updates where the headers are the
# fields and the columns are the profile names
# also maybe include the custom permissions etc


class PackageCreator(object):
    def __init__(self, enviroment, config_manager):
        self.enviroment = enviroment
        self.object_model = read_spreadsheet(enviroment.spreadsheet_path)
        self.config = config_manager
        self.__initialise_package_xml()

    def __initialise_package_xml(self):
        self.package_xml = Xml("Package")
        self.package_xml.set_attribute("xmlns", self.config.sfdc_metadata_xmlns)

    def write_package(self, package_path):
        object_types = Xml("types")
        for sheet_name in self.object_model.get_sheet_names():

            if sheet_name.lower() in self.config.sheets_to_ignore:
                continue

            object_metadata = ObjectMetadataBuilder(sheet_name, self.config)
            object_types.set_field("members", object_metadata.object_api_name)

            self.__write_object_metadata(object_metadata, package_path)

        object_types.set_field("name", "CustomObject")
        self.package_xml.append(object_types)
        self.package_xml.set_field("version", self.enviroment.api_version)
        self.package_xml.write(package_path + "/package.xml")

    def __write_object_metadata(self, object_metadata, package_path):

        object_sheet = self.object_model.get_sheet(object_metadata.object_label)

        while object_sheet.has_more_rows():
            row = object_sheet.get_next_row()
            field = SalesforceField(row)
            object_metadata.add_field(field)

        object_metadata.append_sharing()

        object_metadata.write_metadata(package_path)
