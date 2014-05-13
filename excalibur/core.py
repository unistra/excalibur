# -*- coding: utf-8 -*-
"""
class to run all the process
"""

from excalibur.loader import ConfigurationLoader, PluginLoader
from excalibur.check import CheckACL, CheckArguments, CheckRequest, CheckSource
from excalibur.decode import DecodeArguments
from excalibur.exceptions import PluginRunnerError


class PluginsRunner(object):

    # 22/04/2014 :checksign defaults to false
    def __init__(self, acl_file, sources_file, ressources_file,
                 plugins_module, check_signature=True, check_ip=True,
                 raw_yaml_content=False):
        self.__acl = ConfigurationLoader(acl_file, raw_yaml_content).content
        self.__sources = ConfigurationLoader(sources_file, raw_yaml_content).content
        self.__ressources = ConfigurationLoader(ressources_file, raw_yaml_content).content
        self.__plugins_module = plugins_module
        self.__check_signature = check_signature
        self.__check_ip = check_ip

    @property
    def acl(self):
        return self.__acl

    @property
    def ressources(self):
        return self.__ressources

    @property
    def plugins_module(self):
        return self.__plugins_module

    def plugins(self, source, project=None):
        try:
            return self.sources(project)[source]["plugins"]
        except KeyError:
            raise PluginRunnerError("no such plugin found")

    def sources(self, project=None):
        if project:
            try:
                return self.__sources[project]["sources"]
            except KeyError:
                raise PluginRunnerError("no such source found")
        else:
            return self.__sources

    def sources_names(self, project=None):
        """
        return all sources' names of a project
        """

        if project:
            try:
                return sorted(self.__sources[project]["sources"].keys())
            except KeyError:
                raise PluginRunnerError("no such source found")
        else:
            return sorted(self.__sources.keys())

    def __call__(self, query):
        self.check_all(query)
        data, errors = self.run_plugins(query)
        return data, errors

    def check_all(self, query):
        """
        check all yml
        """
        CheckSource(query, self.sources(query.project),
                    sha1check=self.__check_signature,
                    ipcheck=self.__check_ip)()

        CheckACL(query, self.__acl)()

        CheckRequest(query, self.__ressources)()

        DecodeArguments(query, self.__ressources)()

        CheckArguments(query, self.__ressources)()

    def run_plugins(self, query):
        """
        Parcours les plugins et execute la méthode demandée
        """

        data = {}
        errors = {}
        plugin_loader = PluginLoader(self.__plugins_module)
        if query.project:
            plugins = self.plugins(query.source, query.project)
        else:
            plugins = self.plugins(query.source)

        for plugin_name, parameters_sets in plugins.items():
            for parameters_index, parameters in enumerate(parameters_sets):
                plugin = plugin_loader.get_plugin(plugin_name)
                plugin_data = None
                # Name of the function to run
                f_name = "%s_%s" % (
                    query.ressource, query.method)
                if not hasattr(plugin, f_name):
                    continue  # Ressource/method not implemented in plugin
                try:
                    f = getattr(plugin, f_name)
                    plugin_data = f(parameters, query.arguments)
                except Exception as e:
                    errors[plugin_name] = {'source': query.source,
                                           'ressource': query.ressource,
                                           'method': query.method,
                                           'arguments': query.arguments,
                                           'parameters_index': parameters_index,
                                           'error': e.__class__.__name__,
                                           'error_message':str(e)
                                           }

                if plugin_data is not None:
                    data[plugin_name] = plugin_data

        return data, errors


class Query(object):

    """
    """

    def __init__(self, source, remote_ip, ressource, method, request_method, signature=None, project=None, arguments=None):
        self.__project = project
        self.__source = source
        self.__remote_ip = remote_ip
        self.__signature = signature
        self.__arguments = arguments if arguments else {}
        self.__ressource = ressource
        self.__method = method
        self.__request_method = request_method

    def __str__(self):
        return "project:%s,source:%s,ip:%s,sign:%s,args:%s,ressource:%s,\
method:%s, request_method:%s" % (self.__project, self.__source,
                                 self.__remote_ip, self.__signature,
                                 self.__arguments, self.__ressource,
                                 self.__method, self.__request_method)

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
