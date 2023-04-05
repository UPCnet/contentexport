# -*- coding: utf-8 -*-
from App.config import getConfiguration
from collective.exportimport import _
from collective.exportimport import config
from plone import api

import json
import logging
import os

logger = logging.getLogger(__name__)

from minio import Minio
from minio.error import ResponseError
import s3fs
import boto3


def download(self, data):
    filename = u"{}.json".format(self.__name__)
    if not data:
        msg = _(u"No data to export for {}").format(self.__name__)
        logger.info(msg)
        api.portal.show_message(msg, self.request)
        return self.request.response.redirect(self.request["ACTUAL_URL"])

    if self.download_to_server:
        directory = config.CENTRAL_DIRECTORY
        if directory:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info("Created central export/import directory %s", directory)
        else:
            cfg = getConfiguration()
            portal = api.portal.get()
            directory_import = cfg.clienthome + "/import"
            directory = cfg.clienthome + "/import/" + portal.id
            if directory:
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    logger.info("Created central export/import directory %s", directory)

        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, sort_keys=True, indent=4)

        # from urllib3.util import ssl_
        # context = ssl_.create_urllib3_context()
        # context.options &= ~ssl_.OP_NO_SSLv3

        ACCES_KEY = os.environ.get('access_key', False)
        SECRET_KEY = os.environ.get('secret_key', False)

        # import ipdb; ipdb.set_trace()

        # s3_client = boto3.client(
        #                 'minio.upc.edu',
        #                 aws_access_key_id=ACCES_KEY,
        #                 aws_secret_access_key=SECRET_KEY,
        #                 verify=False,
        #                 config=boto3.session.Config(signature_version='s3v4'),
        #                 region_name='us-east-1'
        #             )

        # response = s3_client.list_objects(Bucket='bucket_name', Prefix=key)
        # boto3.resource(
        #     "s3",
        #     endpoint_url="minio.upc.edu",
        #     aws_access_key_id=ACCES_KEY,
        #     aws_secret_access_key=SECRET_KEY,
        #     verify=False
        # )

        # Connection Minio S3
        client = Minio(
        "minio.upc.edu",
        access_key=ACCES_KEY,
        secret_key=SECRET_KEY,
        secure=False,
        region='us-east-1'
        )


        # Connection S3FS Minio
        fs = s3fs.S3FileSystem(
            anon=False,
            key=ACCES_KEY,
            secret=SECRET_KEY,
            use_ssl=False,
            client_kwargs={
                'endpoint_url': "http://minio.upc.edu" # tried 127.0.0.1:9000 with no success
            }
        )

        #s3 = fs.connect()

        # Create client with custom HTTP client using proxy server.
        # import urllib3
        # client = Minio(
        #     "minio.upc.edu",
        #     access_key="ACCESS_KEY",
        #     secret_key="SECRET_KEY",
        #     secure=True,
        #     region='us-east-1',
        #     http_client=urllib3.ProxyManager(
        #         "minio.upc.edu",
        #         timeout=urllib3.Timeout.DEFAULT_TIMEOUT,
        #         cert_reqs="CERT_REQUIRED",
        #         retries=urllib3.Retry(
        #             total=2,
        #             backoff_factor=0.2,
        #             status_forcelist=[500, 502, 503, 504],
        #         ),
        #     ),
        # )

        # signature_v4 = True
        bucket_name = "genweb6"

        # try:
        #     import ipdb; ipdb.set_trace()
        #     import urllib3.contrib.pyopenssl
        #     urllib3.contrib.pyopenssl.inject_into_urllib3()
        # except ImportError:
        #     pass

        #found = client.bucket_exists(bucket_name)
        found = fs.ls(bucket_name)
        valor = fs.s3.get_object(Bucket=bucket_name, Key='pruebas/export_settings.json')

        results = False

        portal = api.portal.get()

        # # List objects information whose names starts with "my/prefix/".
        # objects = client.list_objects(bucket_name, prefix=portal.id + "/")
        # for obj in objects:
        #     print(obj.bucket_name, obj.object_name, obj.last_modified, \
        #         obj.etag, obj.size, obj.content_type)
        #     # client.remove_object(bucket_name, obj.object_name)
        #     # Download data of an object.
        #     #client.fget_object("genweb6", obj.object_name, str(directory_import) + "/" + obj.object_name)
        #     results = True

        if results == False:
            # objects = client.list_objects(bucket_name, prefix="pruebas")
            # for obj in objects:
            #     print(obj.bucket_name, obj.object_name, obj.last_modified, \
            #         obj.etag, obj.size, obj.content_type)
            # Put an object 'pumaserver_debug.log' with contents from 'pumaserver_debug.log'.
            # try:
            #     client.fput_object("genweb6", str(portal.id + '/' + filename), str(filepath))
            # except ResponseError as err:
            #     print(err)
            # Put a file
            # file_stat = os.stat(filepath)
            # with open(filepath, 'rb') as file_data:
            #     client.put_object(bucket_name, filepath, file_data, file_stat.st_size)
            # file_data.close()
            # with fs.open('genweb6/new-file', 'wb') as f: 
            #     f.write(2*2**20 * b'a')
            #     f.write(2*2**20 * b'a')
            # fichero = fs.du('genweb6/new-file')
            pass

        
        msg = _(u"Exported to {}").format(filepath)
        logger.info(msg)
        api.portal.show_message(msg, self.request)
        return self.request.response.redirect(self.request["ACTUAL_URL"])

    else:
        data = json.dumps(data, sort_keys=True, indent=4)
        data = safe_bytes(data)
        response = self.request.response
        response.setHeader("content-type", "application/json")
        response.setHeader("content-length", len(data))
        response.setHeader(
            "content-disposition",
            'attachment; filename="{0}"'.format(filename),
        )
        return response.write(data)