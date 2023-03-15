# -*- coding: UTF-8 -*-
from collective.exportimport.export_content import ExportContent
from zope.annotation.interfaces import IAnnotations
from plone.restapi.interfaces import IJsonCompatible

import logging

logger = logging.getLogger(__name__)

TYPES_TO_EXPORT = [
    "Folder",
    "Document",
    "Event",
    "File",
    "Image",
    "Link",
    "News Item",
    "Topic",
    "Collection",
    "EasyForm",
    "Banner",
    "BannerContainer",
    "genweb.upc.documentimage",
    "genweb.upc.subhome",
    "LIF",
    "LRF",
    "Logos_Container",
    "Logos_Footer",
    "packet",
]

PATH = ''

# Content for test-migrations
PATHS_TO_EXPORT = []

MARKER_INTERFACES_TO_EXPORT = []

ANNOTATIONS_TO_EXPORT = [
    "genweb.portlets.span.genweb.portlets.HomePortletManager1",
    "genweb.portlets.span.genweb.portlets.HomePortletManager2",
    "genweb.portlets.span.genweb.portlets.HomePortletManager3",
    "genweb.portlets.span.genweb.portlets.HomePortletManager4",
    "genweb.portlets.span.genweb.portlets.HomePortletManager5",
    "genweb.portlets.span.genweb.portlets.HomePortletManager6",
    "genweb.portlets.span.genweb.portlets.HomePortletManager7",
    "genweb.portlets.span.genweb.portlets.HomePortletManager8",
    "genweb.portlets.span.genweb.portlets.HomePortletManager9",
    "genweb.portlets.span.genweb.portlets.HomePortletManager10",
    "genweb.core.important",
    "genweb.packets.fields",
    "genweb.packets.type",
    "genweb.packets.mapui",
]

ANNOTATIONS_KEY = "exportimport.annotations"

MARKER_INTERFACES_KEY = "exportimport.marker_interfaces"


class CustomExportContent(ExportContent):

    QUERY = {
    }

    DROP_PATHS = [
        PATH + '/templates',
        PATH + '/es/shared',
        PATH + '/en/shared',
    ]

    DROP_UIDS = [
    ]

    def update_query(self, query):
        return query

    def update(self):
        self.portal_type = self.portal_type or TYPES_TO_EXPORT

    def global_obj_hook(self, obj):
        """Used this to inspect the content item before serialisation data.
        Bad: Changing the content-item is a bad idea.
        Good: Return None if you want to skip this particular object.
        """
        return obj

    def global_dict_hook(self, item, obj):
        """Used this to modify the serialized data.
        Return None if you want to skip this particular object.
        """
        item = self.export_annotations(item, obj)
        return item

    def export_annotations(self, item, obj):
        results = {}
        annotations = IAnnotations(obj)
        for key in ANNOTATIONS_TO_EXPORT:
            data = annotations.get(key)
            if data:
                results[key] = IJsonCompatible(data, None)
        if results:
            item[ANNOTATIONS_KEY] = results
        return item

    # def export_revisions(self, item, obj):
    #     if not self.include_revisions:
    #         return item
    #     try:
    #         repo_tool = api.portal.get_tool("portal_repository")
    #         history_metadata = repo_tool.getHistoryMetadata(obj)
    #         serializer = getMultiAdapter((obj, self.request), ISerializeToJson)
    #         content_history_viewlet = ContentHistoryViewlet(obj, self.request, None, None)
    #         content_history_viewlet.navigation_root_url = ""
    #         content_history_viewlet.site_url = ""
    #         full_history = content_history_viewlet.fullHistory() or []
    #         history = [i for i in full_history if i["type"] == "versioning"]
    #         if not history or len(history) == 1:
    #             return item
    #         item["exportimport.versions"] = {}
    #         # don't export the current version again
    #         for history_item in history[1:]:
    #             version_id = history_item["version_id"]
    #             item_version = serializer(include_items=False, version=version_id)
    #             item_version = self.update_data_for_migration(item_version, obj)
    #             item["exportimport.versions"][version_id] = item_version
    #             # inject metadata (missing for Archetypes content):
    #             comment = history_metadata.retrieve(version_id)["metadata"]["sys_metadata"]["comment"]
    #             if comment and comment != item["exportimport.versions"][version_id].get("changeNote"):
    #                 item["exportimport.versions"][version_id]["changeNote"] = comment
    #         # current changenote
    #         item["changeNote"] = history_metadata.retrieve(-1)["metadata"]["sys_metadata"]["comment"]
    #         return item
    #     except:
    #         return item
