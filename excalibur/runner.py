# -*- coding: utf-8 -*-
"""
class to run all the process
"""

from excalibur.loader import ConfigurationLoader
from excalibur.utils import check_all, run_plugins

class PluginsRunner(object):

    def __init__(self, acl_file, sources_file, ressources_file, plugins_module, query):
        self.__acl_file = acl_file
        self.__sources_file = sources_file
        self.__ressources_file = ressources_file
        self.__plugins_module = plugins_module
        self.__query = query


    def __call__(self):
        acl = ConfigurationLoader(self.__acl_file).content
        sources = ConfigurationLoader(self.__sources_file).content
        ressources = ConfigurationLoader(self.__ressources_file).content

        check_all(acl, sources, ressources, self.__query)
        data, errors = run_plugins(sources[self.__query['source']]["plugins"], self.__query, self.__plugins_module)

        return data, errors

