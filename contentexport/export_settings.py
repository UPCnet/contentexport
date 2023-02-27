# -*- coding: UTF-8 -*-
import logging

from collective.exportimport.export_other import BaseExport
from plone import api
from plone.restapi.serializer.converters import json_compatible

logger = logging.getLogger(__name__)

#No lo utilizo es un ejemplo de Philip Bauer
class ExportSettings(BaseExport):
    """Export various settings for haiku sites
    """

    def __call__(self, download_to_server=False):
        self.title = "Export installed addons various settings"
        self.download_to_server = download_to_server
        if not self.request.form.get("form.submitted", False):
            return self.index()

        data = self.export_settings()
        self.download(data)

    def export_settings(self):
        results = {}
        addons = []
        qi = api.portal.get_tool("portal_quickinstaller")
        for product in qi.listInstalledProducts():
            if product["id"].startswith("genweb."):
                addons.append(product["id"])
        results["addons"] = addons

        portal = api.portal.get()
        registry = {}
        registry["plone.email_from_name"] = portal.getProperty('email_from_name', '')
        registry["plone.email_from_address"] = portal.getProperty('email_from_address', '')
        registry["plone.smtp_host"] = getattr(portal.MailHost, 'smtp_host', '')
        registry["plone.smtp_port"] = int(getattr(portal.MailHost, 'smtp_port', 25))
        registry["plone.smtp_userid"] = portal.MailHost.get('smtp_user_id')
        registry["plone.smtp_pass"] = portal.MailHost.get('smtp_pass')
        registry["plone.site_title"] = portal.title

        portal_properties = api.portal.get_tool("portal_properties")
        iprops = portal_properties.imaging_properties
        registry["plone.allowed_sizes"] = iprops.getProperty('allowed_sizes')
        registry["plone.quality"] = iprops.getProperty('quality')
        site_props = portal_properties.site_properties
        if site_props.hasProperty("webstats_js"):
            registry["plone.webstats_js"] = site_props.webstats_js
        results["registry"] = json_compatible(registry)
        return results
