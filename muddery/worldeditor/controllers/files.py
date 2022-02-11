"""
Battle commands. They only can be used when a character is in a combat.
"""

import os, tempfile, time
from io import BytesIO
from PIL import Image
from muddery.common.utils.exception import MudderyError, ERR
from muddery.common.networks.responses import success_response, file_response
from muddery.common.utils import writers
from muddery.server.utils import importer
from muddery.worldeditor.controllers.base_request_processer import BaseRequestProcesser
from muddery.worldeditor.dao.image_resources_mapper import ImageResourcesMapper
from muddery.worldeditor.utils.logger import logger
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.services import exporter
from muddery.worldeditor.networks.request_parser import parse_file


class UploadZip(BaseRequestProcesser):
    """
    Upload a zip package of data.

    Args:
        args: None
    """
    path = "upload_zip"
    name = ""

    async def func(self, args, request):
        file_data, origin_name = await parse_file(request)

        if not file_data:
            raise MudderyError(ERR.missing_args, 'Missing zip files.')

        try:
            importer.unzip_data_all(BytesIO(file_data))
        except Exception as e:
            logger.log_trace("Upload error: %s" % e)
            raise MudderyError(ERR.upload_error, str(e))

        return success_response("success")


class UuploadResources(BaseRequestProcesser):
    """
    Upload a zip package of resources.

    Args:
        args: None
    """
    path = "upload_resources"
    name = ""

    async def func(self, args, request):
        file_data, origin_name = await parse_file(request)

        if not file_data:
            raise MudderyError(ERR.missing_args, 'Missing zip files.')

        try:
            importer.unzip_resources_all(BytesIO(file_data))
        except Exception as e:
            logger.log_trace("Upload error: %s" % e)
            raise MudderyError(ERR.upload_error, str(e))

        return success_response("success")


class UploadSingleData(BaseRequestProcesser):
    """
    Upload a data file.

    Args:
        args:
            table: (string) data table's name
    """
    path = "upload_single_data"
    name = ""

    async def func(self, args, request):
        file_data, origin_name = await parse_file(request)

        if not file_data:
            raise MudderyError(ERR.missing_args, 'Missing data files.')

        filename, ext_name = os.path.splitext(origin_name)
        table_name = args.get("table", None)

        if not table_name:
            table_name = filename

        file_type = ""
        if ext_name:
            file_type = ext_name[1:].lower()

        temp_filename = tempfile.mktemp()
        try:
            # Write data to a template file.
            with open(temp_filename, 'wb') as fp:
                fp.write(file_data)
                fp.flush()

                # Import the template file.
                importer.import_file(temp_filename, table_name=table_name, file_type=file_type, clear=True)

                try:
                    os.remove(temp_filename)
                except IOError:
                    pass
        except Exception as e:
            logger.log_trace("Upload error: %s" % e)
            raise MudderyError(ERR.upload_error, str(e))

        return success_response("success")


class DownloadZip(BaseRequestProcesser):
    """
    Download a zip package of data.

    Args:
        args:
            type: (string optional) file type. Default is csv.
    """
    path = "download_zip"
    name = ""

    async def func(self, args, request):
        file_type = args.get("type", "csv")

        # get data's zip
        fp = tempfile.TemporaryFile()
        try:
            exporter.export_zip_all(fp, file_type)
            fp.flush()

            filename = time.strftime("worlddata_%Y%m%d_%H%M%S.zip", time.localtime())
            return await file_response(fp, filename)
        except Exception as e:
            if fp:
                fp.close()
            logger.log_trace("Download error: %s" % e)
            raise MudderyError(ERR.download_error, "Download file error: %s" % e)


class DownloadResources(BaseRequestProcesser):
    """
    Download a zip package of resources.

    Args:
        args: None
    """
    path = "download_resources"
    name = ""

    async def func(self, args, request):
        # get data's zip
        fp = tempfile.TemporaryFile()
        try:
            exporter.export_resources(fp)
            fp.flush()

            filename = time.strftime("resources_%Y%m%d_%H%M%S.zip", time.localtime())
            return await file_response(fp, filename)
        except Exception as e:
            if fp:
                fp.close()
            logger.log_trace("Download error: %s" % e)
            raise MudderyError(ERR.download_error, "Download file error: %s" % e)


class DownloadSingleData(BaseRequestProcesser):
    """
    Export a data table.

    Args:
        args:
            table: (string) table name.
            type: (string optional) file type. Default is csv.
    """
    path = "download_single_data"
    name = ""

    async def func(self, args, request):
        if 'table' not in args:
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
            return await file_response(fp, filename)
        except Exception as e:
            if fp:
                fp.close()
            logger.log_trace("Download error: %s" % e)
            raise MudderyError(ERR.download_error, "Download file error: %s" % e)


class QueryDataFileTypes(BaseRequestProcesser):
    """
    Query available data file types.

    args: None
    """
    path = "query_data_file_types"
    name = ""

    async def func(self, args, request):
        writer_list = writers.get_writers()
        data = [{"type": item.type, "name": item.name} for item in writer_list]
        return success_response(data)


class UploadImage(BaseRequestProcesser):
    """
    Upload a file.

    Args:
        args:
            type: (string) image file's type.
    """
    path = "upload_image"
    name = ""

    async def func(self, args, request):
        file_data, origin_name = await parse_file(request)

        if not file_data:
            raise MudderyError(ERR.missing_args, 'Missing icon files.')

        file_type = args["type"]
        path = os.path.join(SETTINGS.MEDIA_ROOT, SETTINGS.IMAGE_PATH, file_type)
        filepath = os.path.join(path, origin_name)
        exist = False

        if os.path.exists(filepath):
            # remove old file
            os.remove(filepath)
        else:
            if not os.path.exists(path):
                # If does not exist, create one.
                os.makedirs(path)

        # save file
        fp = None
        try:
            fp = open(filepath, "wb+")
            fp.write(file_data)
            fp.flush()
        except Exception as e:
            if fp:
                fp.close()
            logger.log_trace("Upload error: %s" % e)
            raise MudderyError(ERR.upload_error, str(e))

        icon_location = SETTINGS.IMAGE_PATH + "/" + file_type + "/" + origin_name
        try:
            image = Image.open(filepath)
            size = image.size
            ImageResourcesMapper.inst().add(icon_location, file_type, size[0], size[1])
        except Exception as e:
            if fp:
                fp.close()
            logger.log_trace("Upload error: %s" % e)
            raise MudderyError(ERR.upload_error, str(e))

        return success_response({"resource": icon_location})
