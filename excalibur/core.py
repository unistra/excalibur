# -*- coding: utf-8 -*-
"""
class to run all the process
"""

from excalibur.loader import ConfigurationLoader, PluginLoader
from excalibur.check import CheckACL, CheckArguments, CheckRequest, CheckSource
from excalibur.decode import DecodeArguments
from excalibur.exceptions import PluginRunnerError
from importlib import import_module


class PluginsRunner(object):

    # 22/04/2014 :checksign defaults to false

    def __init__(self, acl, sources, ressources,
                 plugins_module, check_signature=True, check_ip=True,
                 raw_yaml_content=False):

        self.__raw_yaml_content = raw_yaml_content

        self["acl"] = acl
        self["sources"] = sources
        self["ressources"] = ressources
        self["plugins_module"] = plugins_module
        self["check_signature"] = check_signature
        self["check_ip"] = check_ip

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

    def __setitem__(self, key, value):
        setattr(self, "_"+self.__class__.__name__+"__" + key,
                self.resolve(value, key))

    def resolve(self, file, key):
        return ConfigurationLoader(file,
                                   self.__raw_yaml_content
                                   ).content if\
            key in ["acl", "sources", "ressources"]\
            else file

    def sources_names(self, project=None):
        """
        Return all sources' names of a project
        """
        if project:
            try:
                return sorted(self.__sources[project]["sources"].keys())
            except KeyError:
                raise PluginRunnerError("no such source found")
        else:
            return sorted(self.__sources.keys())

    def check_all(foo):
        """
        Check all yml
        """

        def checks(self, query):

            module = import_module('excalibur.check')
            check_list = ['CheckSource',
                          'CheckACL',
                          'CheckRequest',
                          'CheckArguments']

            def checker(x):
                checker = getattr(module, x)
                checker(query, self.__ressources,
                        self.sources(query.project),
                        self.__acl,
                        sha1check=self.__check_signature,
                        ipcheck=self.__check_ip)()

            [checker(method_name) for method_name in dir(module) if
                method_name in check_list]

            return foo(self, query)

        return checks

    @check_all
    def __call__(self, query):

        data, errors = self.run_plugins(query)
        return data, errors

    def run_plugins(self, query):
        """
        Browses plugins and executes required method.
        run_plugins is indeed excalibur's core.
        """

        data = {}
        errors = {}

        # Load plugins
        plugin_loader = PluginLoader(self.__plugins_module)

        # Get plugins depending on the sources.yml depth
        plugins = self.plugins(query.source, query.project if
                               query.project else None)

        # Name of the function to run
        f_name = "%s_%s" % (query.ressource, query.method)

        # Actually browse plugins to launch required methods
        # First loop over registered plugins.
        for plugin_name, parameters_sets in plugins.items():
            # Load plugin
            plugin = plugin_loader.get_plugin(plugin_name)
            # Then loop over each plugin registered parameters, with
            # an index so that the error can specify which parameter
            # raised the error.
            for parameters_index, parameters in enumerate(parameters_sets):
                # Initialize returned data to None
                plugin_data = None

                if not hasattr(plugin, f_name):
                    continue  # Ressource/method not implemented in plugin
                # Get data
                try:
                    f = getattr(plugin, f_name)
                    plugin_data = f(parameters, query.arguments)
                # Or register exception
                except Exception as e:
                    errors[plugin_name] = {
                        'source': query.source,
                        'ressource': query.ressource,
                        'method': query.method,
                        'arguments': query.arguments,
                        'parameters_index': parameters_index,
                        'error': e.__class__.__name__,
                        'error_message': str(e)
                    }
                # Register data by plugin name
                if plugin_data is not None:
                    data[plugin_name] = plugin_data

        return data, errors


class Query(object):

    """
    """

    def __init__(self, source,
                 remote_ip,
                 ressource,
                 method,
                 request_method,
                 signature=None,
                 project=None,
                 arguments=None):

        self["project"] = project
        self["source"] = source
        self["remote_ip"] = remote_ip
        self["signature"] = signature
        self["arguments"] = arguments if arguments else {}
        self["ressource"] = ressource
        self["method"] = method
        self["request_method"] = request_method

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

    def __setitem__(self, key, value):
        setattr(self, "_"+self.__class__.__name__+"__" + key,
                value)
