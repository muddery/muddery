"""
This module parse data files to lines.
"""

from __future__ import print_function

import csv

try:
    import xlrd
except ImportError:
    xlrd = None


class DataReader(object):
    """
    Game data file reader.
    """
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
            self.reader = csv.reader(csvfile)
            print("self.reader: %s" % self.reader)

    def readln(self):
        """
        Read data line.

        Returns:
            list: data line
        """
        if not self.reader:
            raise StopIteration

        # read line
        return self.reader.next()


class XLSReader(DataReader):
    """
    CSV file's reader.
    """
    def __init__(self, filename = None):
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
        self.table = None
        self.row_pos = 0
        if filename:
            data = xlrd.open_workbook(filename)
            self.table = data.sheet_by_index(0)

    def readln(self):
        """
        Read data line.

        Returns:
            list: data line
        """
        if not self.table:
            raise StopIteration

        if self.row_pos >= self.table.nrows:
            raise StopIteration

        # read line
        pos = self.row_pos
        self.row_pos += 1
        return self.table.row_values(pos)
