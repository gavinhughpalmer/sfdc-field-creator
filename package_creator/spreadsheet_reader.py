# This provides a facade for the xlrd spreadsheet reader
# so that we can simplify filed access based on the header
# row of the spreadsheet
from xlrd import open_workbook


def parse_boolean(string_to_parse):
    if len(string_to_parse) < 1:
        return False
    first_char = string_to_parse[0].lower()
    return first_char == "y" or first_char == "t"


class Spreadsheet(object):
    def __init__(self, file_path):
        self.spreadsheet = open_workbook(file_path)

    def get_sheet_names(self):
        return self.spreadsheet.sheet_names()

    def get_sheet(self, sheet_name):
        return Sheet(self.spreadsheet, sheet_name)


class Sheet(object):
    def __init__(self, spreadsheet, sheet_name):
        self.spreadsheet = spreadsheet
        self.sheet = spreadsheet.sheet_by_name(sheet_name)
        self.headers = {}
        # Start rows from 1 as the header is 0 indexed
        self.current_row_index = 1
        self.total_rows = self.sheet.nrows
        self.__populate_headers()

    def __populate_headers(self):
        for index, header_cell in enumerate(self.sheet.row(0)):
            self.headers[header_cell.value.lower()] = index

    # counld change to python iterator
    def has_more_rows(self):
        return self.current_row_index < self.total_rows

    def get_next_row(self):
        next_row = Row(self.headers, self.sheet, self.current_row_index)
        self.current_row_index = self.current_row_index + 1
        return next_row


class Row(object):
    def __init__(self, headers, sheet, row_index):
        self.headers = headers
        self.sheet = sheet
        self.row_index = row_index

    def get_cell_value(self, header_name):
        return self.sheet.cell_value(
            self.row_index,
            self.headers.get(header_name.lower())
        )

    def get_cell_bool(self, header_name):
        return parse_boolean(self.get_cell_value(header_name))


def read_spreadsheet(file_path):
    print "Reading Spreadsheet at " + file_path
    return Spreadsheet(file_path)
