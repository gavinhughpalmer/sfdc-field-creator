from xml_writer import Xml
import os
import re


# TODO Test classes...
class MetadataBuilder(object):
    def __init__(self, extension, folder, metadata_label, filename, config_manager):
        self.extension = extension
        self.folder = folder
        self.filename = filename
        self.config = config_manager
        self.__initialise_metadata_xml(metadata_label)

    def __initialise_metadata_xml(self, metadata_label):
        self.metadata_xml = Xml(metadata_label)
        self.metadata_xml.set_attribute("xmlns", self.config.sfdc_metadata_xmlns)

    def write_metadata(self, package_path):
        full_filename = self.filename + "." + self.extension
        metadata_directory = package_path + "/" + self.folder
        self.__create_directory(metadata_directory)
        file_path = metadata_directory + "/" + full_filename
        self.metadata_xml.write(file_path)

    def __create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)


class ObjectMetadataBuilder(MetadataBuilder):
    def __init__(self, object_label, config):
        self.config = config
        self.object_api_name = self.__get_object_api_name(object_label)
        self.object_label = object_label
        self.plural_label = object_label + "s"
        MetadataBuilder.__init__(
            self, "object", "objects", "CustomObject", self.object_api_name, config
        )
        self.__setup_base_file()
        self.__relationships_count = {}
        self.is_detail_object = False

    def __setup_base_file(self):
        if not self.__is_standard_object(self.object_label):
            self.__append_labels()
        self.metadata_xml.set_field("deploymentStatus", "Deployed")

    def __is_standard_object(self, label):
        return label.lower() in self.config.standard_objects

    def __append_labels(self):
        self.metadata_xml.set_field("label", self.object_label)
        self.metadata_xml.set_field("pluralLabel", self.plural_label)

    def add_field(self, field):
        supported_types = self.__get_supported_types_map()
        if field.is_name_field() and field.type == "autonumber":
            self.__append_name_field(field, supported_types)
            return
        elif field.is_standard_picklist():
            # will need to create another metadata type
            return
        elif field.is_standard:
            # nothing to do with standard fields otherwise
            return
        elif field.type not in supported_types:
            print "Field type " + field.type + " not currently supported, skipping"
            return

        field_element = self.__start_field_element(field, supported_types)
        self.__append_type_attributes(field_element, field)
        if field.is_external_id:
            field_element.set_field("externalId", "true")
        if field.is_required:
            field_element.set_field("required", "true")
        if field.type == "picklist":
            self.__append_picklist_values(field_element, field)
        self.metadata_xml.append(field_element)

    def __get_supported_types_map(self):
        supported_types = {}
        for field_type in self.config.field_types["supported_types"]:
            supported_types[field_type.lower()] = field_type
        return supported_types

    def __start_field_element(self, field, supported_types):
        field_element = Xml("fields")
        field_element.set_field("label", field.label)
        field_element.set_field("fullName", self.__get_custom_api_name(field.label))
        field_element.set_field("description", field.description)
        field_element.set_field("inlineHelpText", field.help_text)
        field_element.set_field("type", supported_types[field.type])
        return field_element

    def __append_name_field(self, field, supported_types):
        name_field = Xml("nameField")
        self.__append_autonumber_format(name_field, field)
        name_field.set_field("label", field.label)
        name_field.set_field("type", supported_types[field.type])
        self.metadata_xml.append(name_field)

    def __append_autonumber_format(self, element_to_append, field):
        element_to_append.set_field("displayFormat", field.type_attributes[0])

    # TODO Handle record types
    # TODO move type checks into methods on the field object
    def __append_type_attributes(self, element_to_append, field):
        if field.type in self.config.field_types["text"]:
            element_to_append.set_field("length", field.type_attributes[0])
        elif field.type == "autonumber":
            self.__append_autonumber_format(element_to_append, field)
        elif field.type in self.config.field_types["number"]:
            element_to_append.set_field("precision", field.type_attributes[0])
            element_to_append.set_field("scale", field.type_attributes[1])
        elif field.type == "masterdetail":
            self.__add_relationship(element_to_append, field)
            # TODO should track the relationship order
            element_to_append.set_field("relationshipOrder", "0")
            element_to_append.set_field("reparentableMasterDetail", "false")
            element_to_append.set_field("writeRequiresMasterRead", "false")
            self.is_detail_object = True
        elif field.type == "lookup":
            self.__add_relationship(element_to_append, field)
            element_to_append.set_field("deleteConstraint", "Restrict")
        elif field.type == "checkbox":
            element_to_append.set_field("defaultValue", str(field.default_value).lower())
        else:
            # should throw an error
            pass

    def __add_relationship(self, element_to_append, field):
        element_to_append.set_field("referenceTo", self.__get_object_api_name(field.type_attributes[0]))
        element_to_append.set_field("relationshipLabel", self.plural_label)
        relationship_name = self.plural_label.replace(" ", "_")
        number_of_relationships = 0
        if relationship_name in self.__relationships_count:
            number_of_relationships = self.__relationships_count[relationship_name] + 1
            relationship_name += str(number_of_relationships)
        self.__relationships_count[relationship_name] = number_of_relationships

        element_to_append.set_field("relationshipName", relationship_name)

    def __get_object_api_name(self, label):
        api_name = ""
        if self.__is_standard_object(label):
            api_name = label.replace(" ", "")
        else:
            api_name = self.__get_custom_api_name(label)
        return api_name

    def __get_custom_api_name(self, label):
        if (label.startswith("%")):
            label = "X" + label
        return re.sub(r"[-:_\s%/]+", "_", label) + "__c"

    def __append_picklist_values(self, field_element, field):
        value_set_definition = Xml("valueSetDefinition")
        value_set_definition.set_field("sorted", "true")
        added_values = set()
        for picklist_value in field.values:
            if picklist_value and picklist_value.lower() not in added_values:
                value_set_definition.append(self.__get_picklist_value_node(picklist_value, field.default_value))
                added_values.add(picklist_value.lower())

        value_set = Xml("valueSet")
        value_set.append(value_set_definition)
        field_element.append(value_set)

    def __get_picklist_value_node(self, picklist_value, default_value):
        value_node = Xml("value")
        value_node.set_field("fullName", picklist_value)
        is_default = picklist_value == default_value
        value_node.set_field("default", str(is_default).lower())
        value_node.set_field("label", picklist_value)
        return value_node

    def append_sharing(self):
        # TODO add this based on an attribute elsewhere in the sheet
        if self.object_api_name.lower() != "accountcontactrelation" or self.object_api_name.lower() != "event":
            sharing = "ReadWrite"
            if self.is_detail_object:
                sharing = "ControlledByParent"
            self.metadata_xml.set_field("sharingModel", sharing)
