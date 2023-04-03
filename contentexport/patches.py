# -*- coding: utf-8 -*-
from Acquisition import aq_base
from App.config import getConfiguration
from collective.exportimport import _
from collective.exportimport import config
from OFS.interfaces import IOrderedContainer
from operator import itemgetter
from plone import api
from plone.app.discussion.interfaces import IConversation
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletManager
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.uuid.interfaces import IUUID
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import providedBy

from minio import Minio
from minio.error import ResponseError

import json
import logging
import os
import pkg_resources
import six

try:
    pkg_resources.get_distribution("Products.Archetypes")
except pkg_resources.DistributionNotFound:
    HAS_AT = False
else:
    HAS_AT = True

try:
    pkg_resources.get_distribution("zc.relation")
except pkg_resources.DistributionNotFound:
    HAS_DX = False
else:
    HAS_DX = True

try:
    pkg_resources.get_distribution("z3c.relationfield")
except pkg_resources.DistributionNotFound:
    RelationValue = None
else:
    from z3c.relationfield import RelationValue

try:
    pam_version = pkg_resources.get_distribution("plone.app.multilingual")
    if pam_version.version < "2.0.0":
        IS_PAM_1 = True
    else:
        IS_PAM_1 = False
except pkg_resources.DistributionNotFound:
    IS_PAM_1 = False

logger = logging.getLogger(__name__)

PORTAL_PLACEHOLDER = "<Portal>"

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
            directory = cfg.clienthome

        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, sort_keys=True, indent=4)

        # from urllib3.util import ssl_
        # context = ssl_.create_urllib3_context()
        # context.options &= ~ssl_.OP_NO_SSLv3

        ACCES_KEY = os.environ.get('access_key', False)
        SECRET_KEY = os.environ.get('secret_key', False)

        # Connection Minio S3
        client = Minio(
        "minio.upc.edu",
        access_key=ACCES_KEY,
        secret_key=SECRET_KEY,
        secure=False,
        region='us-east-1'
        )

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
        import ipdb; ipdb.set_trace()
        # try:
        #     import ipdb; ipdb.set_trace()
        #     import urllib3.contrib.pyopenssl
        #     urllib3.contrib.pyopenssl.inject_into_urllib3()
        # except ImportError:
        #     pass

        #found = client.bucket_exists(bucket_name)
    

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
            try:
                client.fput_object("genweb6", str(portal.id + '/' + filename), str(filepath))
            except ResponseError as err:
                print(err)
            # Put a file
            # file_stat = os.stat(filepath)
            # with open(filepath, 'rb') as file_data:
            #     client.put_object(bucket_name, filepath, file_data, file_stat.st_size)
            # file_data.close()               
        
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