"""
This module parse data files to lines.
"""

from __future__ import print_function

import csv

try:
    import xlrd
except ImportError:
    xlrd = None


def csv_reader(file_name):
    """
    Parse csv files.

    Args:
        file_name: (string) csv file's name.
    """
    # load file
    csvfile = open(file_name, 'r')
    reader = csv.reader(csvfile)

    # read lines
    while True:
        yield reader.next()


def xls_reader(file_name):
    """
    Parse xls files.

    Args:
        file_name: (string) xls file's name.
    """
    if not xlrd:
        print('**********************************************************')
        print('You need to install "xlrd" first to import xls/xlsx files!')
        print('You can use "pip install xlrd" to install it!             ')
        print('**********************************************************')
        return

    # load file
    data = xlrd.open_workbook(file_name)
    table = data.sheet_by_index(0)

    # read lines
    for i in range(table.nrows):
        yield table.row_values(i)
