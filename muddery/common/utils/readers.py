"""
This module parse data files to lines.
"""

import csv
import xlrd


class DataReader(object):
    """
    Game data file reader.
    """
    types = None

    def __init__(self, filename = None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        self.filename = filename

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        return self.readln()

    def readln(self):
        """
        Read data line.

        Returns:
            list: data line
        """
        # No data.
        raise StopIteration

    def close(self):
        """
        Close the file.
        """
        pass


class CSVReader(DataReader):
    """
    CSV file's reader.
    """
    types = ("csv",)

    def __init__(self, filename=None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        super(CSVReader, self).__init__(filename)

        self.reader = None
        self.csvfile = None

        if filename:
            try:
                self.csvfile = open(filename, 'r', encoding='utf-8-sig')
            except UnicodeDecodeError:
                self.csvfile = open(filename, 'r')

            self.reader = csv.reader(self.csvfile)

    def readln(self):
        """
        Read data line.

        Returns:
            list: data line
        """
        if not self.reader:
            raise StopIteration

        # Read line.
        return next(self.reader)

    def close(self):
        """
        Close the file.
        """
        if self.csvfile:
            self.csvfile.close()


class XLSReader(DataReader):
    """
    XLS/XLSX file's reader.
    """
    types = ("xls", "xlsx")

    def __init__(self, filename=None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        super(XLSReader, self).__init__(filename)

        # load file
        self.sheet = None
        self.row_pos = 0
        self.book = None
        self.sheet = None

        if filename:
            self.book = xlrd.open_workbook(filename)
            self.sheet = self.book.sheet_by_index(0)

    def readln(self):
        """
        Read data line.

        Returns:
            list: data line
        """
        if not self.sheet:
            raise StopIteration

        if self.row_pos >= self.sheet.nrows:
            raise StopIteration

        # Read line.
        pos = self.row_pos
        self.row_pos += 1
        return self.sheet.row_values(pos)


all_readers = [CSVReader, XLSReader]
def get_readers():
    """
    Get all available writers.

    Returns:
        list: available writers
    """
    return all_readers


reader_dict = {type: reader for reader in all_readers for type in reader.types}
def get_reader(reader_type):
    """
    Get a reader by reader's type.

    Args:
        type: (String) reader's type.

    Returns:
        reader
    """
    return reader_dict.get(reader_type, None)
