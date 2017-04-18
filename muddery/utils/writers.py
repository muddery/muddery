"""
This module parse data files to lines.
"""

from __future__ import print_function

import csv
import codecs

try:
    import xlwt
except ImportError:
    xlwt = None

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class DataWriter(object):
    """
    Game data file writer.
    """
    type = None
    name = None
    file_ext = None

    def __init__(self, filename = None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        self.filename = filename

    def writeln(self, line):
        """
        Write data line.

        Args:
            line: (List) Line data.

        Returns:
            boolean: Write success.
        """
        # No data.
        return False

    def save(self):
        """
        Save the file

        Returns:
            None
        """
        pass


class CSVWriter(DataWriter):
    """
    CSV file's writer.
    """
    type = "csv"
    name = "csv"
    file_ext = "csv"

    def __init__(self, filename=None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        super(CSVWriter, self).__init__(filename)

        self.data_file = None
        self.writer = None
        if filename:
            self.data_file = open(filename, 'w')
            self.writer = csv.writer(self.data_file, dialect='excel')

    def writeln(self, line):
        """
        Write data line.

        Args:
            line: (List) Line data.

        Returns:
            boolean: Write success.
        """
        if not self.writer:
            return False

        # Write line.
        self.writer.writerow(line)
        return True

    def save(self):
        """
        Save the file

        Returns:
            None
        """
        if not self.data_file:
            return

        self.data_file.close()


class CSVWindowsWriter(DataWriter):
    """
    CSV file's writer.
    """
    type = "csv_win"
    name = "csv (For Windows)"
    file_ext = "csv"

    def __init__(self, filename=None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        super(CSVWindowsWriter, self).__init__(filename)

        self.data_file = None
        self.writer = None
        if filename:
            self.data_file = open(filename, 'w')
            self.data_file.write(codecs.BOM_UTF8)
            self.writer = csv.writer(self.data_file, dialect='excel')

    def writeln(self, line):
        """
        Write data line.

        Args:
            line: (List) Line data.

        Returns:
            boolean: Write success.
        """
        if not self.writer:
            return False

        # Write line.
        self.writer.writerow(line)
        return True

    def save(self):
        """
        Save the file

        Returns:
            None
        """
        if not self.data_file:
            return

        self.data_file.close()


class XLSWriter(DataWriter):
    """
    XLS/XLSX file's writer.
    
    IT HAS PROBLEMS ON WINDOWS!
    """
    type = "xls"
    name = "xls"
    file_ext = "xls"

    def __init__(self, filename=None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        super(XLSWriter, self).__init__(filename)

        if not xlwt:
            print('**********************************************************')
            print('You need to install "xlwt" first to export xls files!')
            print('You can use "pip install xlwt" to install it!             ')
            print('**********************************************************')
            return

        # create file
        self.book = None
        self.sheet = None
        self.row_pos = 0
        if filename:
            self.book = xlwt.Workbook(encoding='utf-8')
            self.sheet = self.book.add_sheet("sheet 1")

    def writeln(self, line):
        """
        Write data line.

        Args:
            line: (List) Line data.

        Returns:
            boolean: Write success.
        """
        if not self.sheet:
            return False

        # write line
        for index, item in enumerate(line):
            self.sheet.write(self.row_pos, index, item)

        self.row_pos += 1
        return True

    def save(self):
        """
        Save the file

        Returns:
            None
        """
        if not self.book:
            return

        self.book.save(self.filename)


class XLSXWriter(DataWriter):
    """
    XLSX file's writer.
    
    IT HAS PROBLEMS ON WINDOWS!
    """
    type = "xlsx"
    name = "xlsx"
    file_ext = "xlsx"

    def __init__(self, filename=None):
        """
        Args:
            filename: (String) data file's name.

        Returns:
            None
        """
        super(XLSXWriter, self).__init__(filename)

        if not xlwt:
            print('**********************************************************')
            print('You need to install "xlsxwriter" first to export xlsx files!')
            print('You can use "pip install xlsxw'
                  'riter" to install it!         ')
            print('**********************************************************')
            return

        # create file
        self.book = None
        self.sheet = None
        self.row_pos = 0
        if filename:
            self.book = xlsxwriter.Workbook(filename)
            self.sheet = self.book.add_worksheet("sheet 1")

    def writeln(self, line):
        """
        Write data line.

        Args:
            line: (List) Line data.

        Returns:
            boolean: Write success.
        """
        if not self.sheet:
            return False

        # write line
        self.sheet.write_row(self.row_pos, 0, line)

        self.row_pos += 1
        return True

    def save(self):
        """
        Save the file

        Returns:
            None
        """
        if not self.book:
            return

        self.book.close()


all_writers = [CSVWindowsWriter, CSVWriter, XLSWriter]
def get_writers():
    """
    Get all available writers.

    Returns:
        list: available writers
    """
    return all_writers


writer_dict = {writer.type: writer for writer in all_writers}
def get_writer(writer_type):
    """
    Get a writer by writer's type.

    Args:
        type: (String) writer's type.

    Returns:
        writer
    """
    return writer_dict.get(writer_type, None)
