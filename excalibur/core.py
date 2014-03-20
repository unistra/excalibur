# -*- coding: utf-8 -*-
"""
class to run all the process
"""

from excalibur.loader import ConfigurationLoader, PluginLoader
from excalibur.check import CheckACL, CheckArguments, CheckRequest, CheckSource
from excalibur.decode import DecodeArguments


class PluginsRunner(object):

    def __init__(self, acl_file, sources_file, ressources_file, plugins_module, query):
        self.__acl = ConfigurationLoader(acl_file).content
        self.__sources = ConfigurationLoader(sources_file).content
        self.__ressources = ConfigurationLoader(ressources_file).content
        self.__plugins_module = plugins_module
        self.__query = query

    @property
    def plugins(self):
        return self.sources[self.__query.source]["plugins"]

    @property
    def acl(self):
        return self.__acl

    @property
    def sources(self):
        if self.__query.project:
            return self.__sources[self.__query.project]["sources"]
        else:
            return self.__sources

    @property
    def ressources(self):
        return self.__ressources

    @property
    def plugins_module(self):
        return self.__plugins_module

    @property
    def query(self):
        return self.__query

    def __call__(self):
        self.check_all()
        data, errors = self.run_plugins()
        return data, errors

    def check_all(self):
        """
        check all yml
        """

        check_source = CheckSource(self.sources)
        check_source.check(self.__query.source, self.__query.remote_ip,
                           self.__query.signature, self.__query.arguments)

        check_acl = CheckACL(self.__acl)
        check_acl.check(self.__query.source, self.__query.ressource,
                        self.__query.method, self.__query.project)

        check_request = CheckRequest(self.__ressources)
        check_request.check(
            self.__query.request_method, self.__query.ressource, self.__query.method, self.__query.arguments)

        decode_arguments = DecodeArguments(self.__ressources)
        decode_arguments.decode(
            self.__query.ressource, self.__query.method, self.__query.arguments)

        check_arguments = CheckArguments(self.__ressources)
        check_arguments.check(
            self.__query.arguments, self.__query.ressource, self.__query.method)

    def run_plugins(self):
        """
        Parcours les plugins et execute la méthode demandée
        """

        data = {}
        errors = {}
        plugin_loader = PluginLoader(self.__plugins_module)

        for plugin_name, parameters_sets in self.plugins.items():
            for parameters_index, parameters in enumerate(parameters_sets):
                plugin = plugin_loader.get_plugin(plugin_name)
                plugin_data = None
                # Name of the function to run
                f_name = "%s_%s" % (
                    self.__query.ressource, self.__query.method)
                if not hasattr(plugin, f_name):
                    continue  # Ressource/method not implemented in plugin
                try:
                    f = getattr(plugin, f_name)
                    plugin_data = f(parameters, self.__query.arguments)
                except Exception as e:
                    errors[plugin_name] = {'source': self.__query.source,
                                           'ressource': self.__query.ressource,
                                           'method': self.__query.method,
                                           'arguments': self.__query.arguments,
                                           'parameters_index': parameters_index,
                                           'error': e.__class__.__name__
                                           }

                if plugin_data is not None:
                    data[plugin_name] = plugin_data

        return data, errors


class Query(object):

    """
    """

    def __init__(self, source, remote_ip, signature, ressource, method, request_method, project=None, arguments=None):
        self.__project = project
        self.__source = source
        self.__remote_ip = remote_ip
        self.__signature = signature
        self.__arguments = arguments if arguments else {}
        self.__ressource = ressource
        self.__method = method
        self.__request_method = request_method

    def __str__(self):
        return dir(self)

    @property
    def project(self):
        return self.__project

    @property
    def source(self):
        return self.__source

    @property
    def remote_ip(self):
        return self.__remote_ip

    @property
    def signature(self):
        return self.__signature

    @property
    def arguments(self):
        return self.__arguments

    @property
    def ressource(self):
        return self.__ressource

    @property
    def method(self):
        return self.__method

    @property
    def request_method(self):
        return self.__request_method
