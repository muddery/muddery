"""
This module parse data files to lines.
"""

from __future__ import print_function

import csv
import codecs

try:
    import xlrd
except ImportError:
    xlrd = None


class DataReader(object):
    """
    Game data file reader.
    """
    available_types = None

    def __init__(self, filename = None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        self.filename = filename

    def readln(self):
        """
        Read data line.

        Returns:
            list: data line
        """
        # No data.
        raise StopIteration


class CSVReader(DataReader):
    """
    CSV file's reader.
    """
    available_types = ("csv",)

    def __init__(self, filename=None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        super(CSVReader, self).__init__(filename)

        self.reader = None
        if filename:
            csvfile = open(filename, 'r')

            # test BOM
            head = csvfile.read(len(codecs.BOM_UTF8))
            if head != codecs.BOM_UTF8:
                # read from beginning
                csvfile.seek(0)
            self.reader = csv.reader(csvfile)

    def readln(self):
        """
        Read data line.

        Returns:
            list: data line
        """
        if not self.reader:
            raise StopIteration

        # Read line.
        return self.reader.next()


class XLSReader(DataReader):
    """
    XLS/XLSX file's reader.
    """
    available_types = ("xls", "xlsx")

    def __init__(self, filename=None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        super(XLSReader, self).__init__(filename)

        if not xlrd:
            print('**********************************************************')
            print('You need to install "xlrd" first to import xls/xlsx files!')
            print('You can use "pip install xlrd" to install it!             ')
            print('**********************************************************')
            return

        # load file
        self.sheet = None
        self.row_pos = 0
        if filename:
            book = xlrd.open_workbook(filename)
            self.sheet = book.sheet_by_index(0)

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


def get_readers():
    """
    Get all available writers.

    Returns:
        list: available writers
    """
    readers = [CSVReader]
    if xlrd:
        readers.append(XLSReader)

    return readers