# -*- coding: UTF-8 -*-
import logging

from collective.exportimport.export_other import BaseExport
from plone import api
from plone.restapi.serializer.converters import json_compatible
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from genweb.controlpanel.interface import IGenwebControlPanelSettings 

logger = logging.getLogger(__name__)

class ExportControlpanels(BaseExport):
    """Export various controlpanels 
    """

    def __call__(self, download_to_server=False):
        self.title = "Export installed addons various settings"
        self.download_to_server = download_to_server
        if not self.request.form.get("form.submitted", False):
            return self.index()

        data = self.export_cotrolpanels()
        self.download(data)

    def export_cotrolpanels(self):
        results = {}
        addons = []
        qi = api.portal.get_tool("portal_quickinstaller")
        for product in qi.listInstalledProducts():
            if product["id"].startswith("genweb."):
                addons.append(product["id"])
        results["addons"] = addons

        portal = api.portal.get()
        controlpanel = {}
        gwsettings = getUtility(IRegistry).forInterface(IGenwebControlPanelSettings)
        controlpanel["genweb6.core.controlpanels.footer.IFooterSettings"]=dict(signatura_ca=gwsettings.signatura_unitat_ca,
                                                                               signatura_es=gwsettings.signatura_unitat_es,
                                                                               signatura_en=gwsettings.signatura_unitat_en)
        controlpanel["genweb6.core.controlpanels.header.IHeaderSettings"]=dict(main_hero_style='text-hero' if gwsettings.treu_imatge_capsalera == 'True' else 'image-hero',
                                                                               content_hero_style='text-hero' if gwsettings.treu_imatge_capsalera == 'True' else 'image-hero',
                                                                               html_title_ca=gwsettings.html_title_ca,
                                                                               html_title_es=gwsettings.html_title_es,
                                                                               html_title_en=gwsettings.html_title_en,
                                                                               treu_menu_horitzontal=gwsettings.treu_menu_horitzontal,
                                                                               amaga_identificacio=gwsettings.amaga_identificacio,
                                                                               idiomes_publicats=gwsettings.idiomes_publicats,
                                                                               languages_link_to_root=gwsettings.languages_link_to_root)
        controlpanel["genweb6.upc.controlpanels.upc.IUPCSettings"]=dict(contacte_al_peu=gwsettings.contacte_al_peu,
                                                                        contacte_id=gwsettings.contacte_id,
                                                                        contacte_BBDD_or_page=gwsettings.contacte_BBDD_or_page,
                                                                        contacte_multi_email=gwsettings.contacte_multi_email,
                                                                        contact_emails_table=gwsettings.contact_emails_table)
        results["controlpanel"] = json_compatible(controlpanel)
        return results
