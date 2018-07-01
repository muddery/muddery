"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

import os, tempfile, time, shutil, filecmp
from PIL import Image
from django.conf import settings
from django.contrib import auth
from evennia.utils import logger
from muddery.worlddata.services import data_query, exporter, importer
from muddery.worlddata.utils.response import success_response, file_response
from muddery.utils.exception import MudderyError, ERR
from muddery.utils import writers
from muddery.worlddata.controllers.base_request_processer import BaseRequestProcesser
from muddery.worlddata.dao.image_resources_mapper import IMAGE_RESOURCES


class upload_zip(BaseRequestProcesser):
    """
    Upload a zip package of data.

    Args:
        args: None
    """
    path = "upload_zip"
    name = ""

    def func(self, args, request):
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


class upload_resources(BaseRequestProcesser):
    """
    Upload a zip package of resources.

    Args:
        args: None
    """
    path = "upload_resources"
    name = ""

    def func(self, args, request):
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


class upload_single_data(BaseRequestProcesser):
    """
    Upload a data file.

    Args:
        args:
            table: (string) data table's name
    """
    path = "upload_single_data"
    name = ""

    def func(self, args, request):
        file_obj = request.FILES.get("file", None)

        if not file_obj:
            raise MudderyError(ERR.missing_args, 'Missing data files.')

        fullname = file_obj.name
        filename, ext_name = os.path.splitext(fullname)
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


class download_zip(BaseRequestProcesser):
    """
    Download a zip package of data.

    Args:
        args:
            type: (string optional) file type. Default is csv.
    """
    path = "download_zip"
    name = ""

    def func(self, args, request):
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


class download_resources(BaseRequestProcesser):
    """
    Download a zip package of resources.

    Args:
        args: None
    """
    path = "download_resources"
    name = ""

    def func(self, args, request):
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


class download_single_data(BaseRequestProcesser):
    """
    Export a data table.

    Args:
        args:
            table: (string) table name.
            type: (string optional) file type. Default is csv.
    """
    path = "download_single_data"
    name = ""

    def func(self, args, request):
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


class query_data_file_types(BaseRequestProcesser):
    """
    Query available data file types.

    args: None
    """
    path = "query_data_file_types"
    name = ""

    def func(self, args, request):
        writer_list = writers.get_writers()
        data = [{"type": item.type, "name": item.name} for item in writer_list]
        return success_response(data)


class upload_image(BaseRequestProcesser):
    """
    Upload a file.

    Args:
        args:
            type: (string) image file's type.
    """
    path = "upload_image"
    name = ""

    def func(self, args, request):
        file_obj = request.FILES.get("file", None)

        if not file_obj:
            raise MudderyError(ERR.missing_args, 'Missing icon files.')

        file_type = args["type"]
        filename = file_obj.name
        path = os.path.join(settings.MEDIA_ROOT, settings.IMAGE_PATH, file_type)
        filepath = os.path.join(path, filename)
        exist = False

        if not os.path.exists(filepath):

            if not os.path.exists(path):
                # If does not exist, create one.
                os.makedirs(path)

            # save file
            fp = None
            try:
                fp = open(filepath, "wb+")
                for chunk in file_obj.chunks():
                    fp.write(chunk)
                fp.flush()
            except Exception, e:
                if fp:
                    fp.close()
                logger.log_tracemsg("Upload error: %s" % e.message)
                raise MudderyError(ERR.upload_error, e.message)
        else:
            # Compare the uploaded file with the local file.
            with tempfile.NamedTemporaryFile() as fp:
                try:
                    for chunk in file_obj.chunks():
                        fp.write(chunk)
                    fp.flush()

                    same = filecmp.cmp(filepath, fp.name)
                    if not same:
                        raise MudderyError(ERR.upload_image_exist, 'File %s already exists.' % filename)

                    exist = True
                except Exception, e:
                    logger.log_tracemsg("Upload error: %s" % e.message)
                    raise MudderyError(ERR.upload_error, e.message)

        icon_location = settings.IMAGE_PATH + "/" + file_type + "/" + filename
        if not exist:
            try:
                image = Image.open(filepath)
                size = image.size

                IMAGE_RESOURCES.add(icon_location, file_type, size[0], size[1])
            except Exception, e:
                if fp:
                    fp.close()
                logger.log_tracemsg("Upload error: %s" % e.message)
                raise MudderyError(ERR.upload_error, e.message)

        return success_response({"resource": icon_location})
