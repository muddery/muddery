"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

import os, tempfile, time
from django.conf import settings
from django.contrib import auth
from evennia.utils import logger
from muddery.mappings.request_set import request_mapping
from muddery.worlddata.service import data_query, exporter, importer
from muddery.worlddata.utils.response import success_response, file_response
from muddery.utils.exception import MudderyError, ERR
from muddery.utils import writers


@request_mapping
def upload_zip(args, request):
    """
    Upload a zip package of data.

    Args:
        args: None
    """
    file_obj = request.FILES.get("file", None)

    if not file_obj:
        raise MudderyError(ERR.missing_args, 'Missing zip files.')

    with tempfile.TemporaryFile() as fp:
        try:
            for chunk in file_obj.chunks():
                fp.write(chunk)
            importer.unzip_data_all(fp)
        except Exception, e:
            logger.log_tracemsg("Upload error: %s" % e.message)
            raise MudderyError(ERR.upload_error, e.message)

    return success_response("success")


@request_mapping
def upload_resources(args, request):
    """
    Upload a zip package of resources.

    Args:
        args: None
    """
    file_obj = request.FILES.get("file", None)

    if not file_obj:
        raise MudderyError(ERR.missing_args, 'Missing zip files.')

    with tempfile.TemporaryFile() as fp:
        try:
            for chunk in file_obj.chunks():
                fp.write(chunk)
            importer.unzip_resources_all(fp)
        except Exception, e:
            logger.log_tracemsg("Upload error: %s" % e.message)
            raise MudderyError(ERR.upload_error, e.message)

    return success_response("success")


@request_mapping
def upload_single_data(args, request):
    """
    Upload a data file.

    Args:
        args:
            table: (string) data table's name
    """
    file_obj = request.FILES.get("file", None)

    if not file_obj:
        raise MudderyError(ERR.missing_args, 'Missing data files.')

    fullname = file_obj.name
    (filename, ext_name) = os.path.splitext(fullname)
    table_name = args.get("table", None)

    if not table_name:
        table_name = filename

    file_type = ""
    if ext_name:
        file_type = ext_name[1:].lower()

    with tempfile.NamedTemporaryFile() as fp:
        try:
            for chunk in file_obj.chunks():
                fp.write(chunk)
            importer.import_data_file(fp, table_name=table_name, file_type=file_type)
        except Exception, e:
            logger.log_tracemsg("Upload error: %s" % e.message)
            raise MudderyError(ERR.upload_error, e.message)

    return success_response("success")


@request_mapping
def download_zip(args, request):
    """
    Download a zip package of data.

    Args:
        args:
            type: (string optional) file type. Default is csv.
    """
    file_type = args.get("type", "csv")

    # get data's zip
    fp = tempfile.TemporaryFile()
    try:
        exporter.export_zip_all(fp, file_type)
        fp.seek(0)

        filename = time.strftime("worlddata_%Y%m%d_%H%M%S.zip", time.localtime())
        return file_response(fp, filename)
    except Exception, e:
        if fp:
            fp.close()
        logger.log_tracemsg("Download error: %s" % e.message)
        raise MudderyError(ERR.download_error, "Download file error: %s" % e)


@request_mapping
def download_resources(args, request):
    """
    Download a zip package of resources.

    Args:
        args: None
    """
    # get data's zip
    fp = tempfile.TemporaryFile()
    try:
        exporter.export_resources(fp)
        fp.seek(0)

        filename = time.strftime("resources_%Y%m%d_%H%M%S.zip", time.localtime())
        return file_response(fp, filename)
    except Exception, e:
        if fp:
            fp.close()
        logger.log_tracemsg("Download error: %s" % e.message)
        raise MudderyError(ERR.download_error, "Download file error: %s" % e)


@request_mapping
def download_single_data(args, request):
    """
    Export a data table.

    Args:
        args:
            table: (string) table name.
            type: (string optional) file type. Default is csv.
    """
    if ('table' not in args):
        raise MudderyError(ERR.missing_args, 'Missing the table name.')

    table_name = args['table']
    file_type = args.get("type", "csv")

    writer_class = writers.get_writer(file_type)
    if not writer_class:
        raise MudderyError(ERR.download_error, "Unknown file type: %s" % file_type)

    # Get tempfile's name.
    temp_name = tempfile.mktemp()
    exporter.export_file(temp_name, table_name, file_type)
    fp = open(temp_name, "rb")
    try:
        filename = table_name + "." + writer_class.file_ext
        return file_response(fp, filename)
    except Exception, e:
        if fp:
            fp.close()
        logger.log_tracemsg("Download error: %s" % e.message)
        raise MudderyError(ERR.download_error, "Download file error: %s" % e)


@request_mapping
def query_data_file_types(args, request):
    """
    Query available data file types.

    args: None
    """
    writer_list = writers.get_writers()
    data = [{"type": item.type, "name": item.name} for item in writer_list]
    return success_response(data)


