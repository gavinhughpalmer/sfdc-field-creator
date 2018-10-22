import re


FIELD_TYPE_PATTERN = re.compile(r"(\w*)\s*\(\s*([\d\w]*[-{},\d\w\s]*)\)")


# TODO include the header columns in a settings document so this can be easily modified...
# TODO create distinct settings files
class SalesforceField(object):
    def __init__(self, row):
        # TODO trim values and potentially the picklist values...
        self.label = row.get_cell_value("field name").strip()
        self.is_standard = row.get_cell_bool("standard")
        self.description = row.get_cell_value("description")
        self.help_text = row.get_cell_value("help text")
        self.is_external_id = row.get_cell_bool("unique key")
        self.field_type = row.get_cell_value("type")
        if self.field_type.lower() == "checkbox":
            self.default_value = row.get_cell_bool("default")
        else:
            self.default_value = row.get_cell_value("default")
        self.values = [x.strip() for x in row.get_cell_value("values").split("\n")]
        self.type = self.field_type
        self.type_attributes = []
        self.__populate_type_attributes()
        self.is_required = row.get_cell_bool("required") and self.type.lower() != "masterdetail"

    def __populate_type_attributes(self):
        match_result = FIELD_TYPE_PATTERN.match(self.field_type)
        if match_result:
            self.type = match_result.group(1)
            if match_result.group(2):
                self.type_attributes = [x.strip() for x in match_result.group(2).split(",")]
        self.type = self.type.lower().strip()

    def is_name_field(self):
        return self.is_standard and self.label.lower() == "name"

    def is_standard_picklist(self):
        return self.is_standard and self.type == "picklist"

        # TODO could include an append to sheet method that addsthe fields to a spreadsheet so that we can go both ways
