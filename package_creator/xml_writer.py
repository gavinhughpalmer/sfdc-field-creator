# A facade for the lxml etree so that we can easily
# write xml files and append to the xml
from lxml import etree

PRETTY_PRINT_XML = True


class Xml(object):
    def __init__(self, element_name):
        self.element = etree.Element(element_name)

    def set_attribute(self, attribute, value):
        self.element.set(attribute, value)

    def set_field(self, field_name, value):
        etree.SubElement(self.element, field_name).text = value

    def append(self, element_to_append):
        self.element.append(element_to_append.element)

    def to_string(self):
        return etree.tostring(
            self.element,
            xml_declaration=True,
            encoding="UTF-8",
            with_tail=True,
            pretty_print=PRETTY_PRINT_XML
        )

    def write(self, file_path):
        with open(file_path, "w+") as package_file:
            package_file.write(self.to_string())
