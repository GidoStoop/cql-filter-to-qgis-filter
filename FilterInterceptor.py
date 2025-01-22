
# coding=utf-8
"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

"""

__author__ = 'gidostoop9@gmailcom'
__date__ = '2024-12-06'


from qgis.server import QgsServerFilter
from qgis.core import QgsMessageLog
from qgis.server import *
from .utils.CqlFilterToQgisUtil import cql_filter_string_to_qgis_filter_string

class FilterInterceptorService(QgsServerFilter):

    def __init__(self, serverIface):
        super(FilterInterceptorService, self).__init__(serverIface)

    def onRequestReady(self) -> bool:
        request = self.serverInterface().requestHandler()
        params = request.parameterMap( )
        if 'CQL_FILTER' in params and params['SERVICE'] == 'WMS':
            cql_filter_string = params['CQL_FILTER']

            qgis_filter_string = cql_filter_string_to_qgis_filter_string(cql_filter_string, params)
            request.removeParameter("CQL_FILTER")
            request.setParameter('FILTER', qgis_filter_string)
            QgsMessageLog.logMessage(qgis_filter_string)
        return True

    def onResponseComplete(self) -> bool:
        request = self.serverInterface().requestHandler()
        params = request.parameterMap( )
        if 'CQL_FILTER' in params:
            QgsMessageLog.logMessage("Plugin: CQL-Filter intercepted and parsed as QGIS server Filter")
        return True

        
class FilterInterceptor():

    def __init__(self, serverIface):
        self.serv = FilterInterceptorService(serverIface)
        serverIface.registerFilter(self.serv)