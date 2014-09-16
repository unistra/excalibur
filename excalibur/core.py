# -*- coding: utf-8 -*-
"""
class to run all the process
"""

from excalibur.loader import ConfigurationLoader, PluginLoader
from excalibur.check import CheckACL,\
    CheckArguments, CheckRequest, CheckSource
from excalibur.decode import DecodeArguments
from excalibur.exceptions import PluginRunnerError, WrongSignatureError
from importlib import import_module
import base64
import hashlib
from functools import reduce
from excalibur.utils import add_args_then_encode, get_api_keys, ALL_KEYWORD,\
    PLUGIN_NAME_SEPARATOR, SOURCE_SEPARATOR
from excalibur.conf import Sources


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

    def plugins(self, source, signature, arguments=None, project=None):
        """
        returns allowed plugins
        """
        try:
            if source != ALL_KEYWORD and SOURCE_SEPARATOR not in source:

                return self.sources(signature,
                                    project,
                                    arguments)[source]["plugins"]
            else:
                targeted_sources = self.sources(signature,
                                                project,
                                                arguments)
                formatedPluginsList = {}
                for k, v in targeted_sources.items():
                    for clef, valeur in v['plugins'].items():
                        formatedPluginsList[
                            k + PLUGIN_NAME_SEPARATOR + clef] = valeur

                return formatedPluginsList
        except KeyError as k:
            raise PluginRunnerError("no such plugin found")

    def sources(self, signature, project=None, arguments=None):
        """
        Since the sources are either registered at top-level
        in the matching yml file or distibuted by projects
        sources() works as a filter to return either the whole
        yml, or the matching entries.
        """

        if project:
            try:
                project = self.__sources[project]
#                 if there is at least one source that contains
#                 an apikey specification.
                if [it["apikey"] for
                    it in list(project["sources"].values()) if
                        "apikey" in
                        list(it.keys())] and self.__check_signature:
                    api_keys = get_api_keys(
                        list(project["sources"].values()), arguments)

                    targeted_sources = project["sources"] if signature in\
                        api_keys else None
                    if not targeted_sources:
                        raise WrongSignatureError(signature)
                    return project["sources"] if\
                        signature in api_keys else None

#                 if there is no apikey entry in any of the configured sources
#                 it means that the apikey authentification is not used by
#                 the app, and that all sources are allowed sources.
                else:
                    # here a more precise subselection could be done.
                    return project["sources"]
            except KeyError as k:
                raise PluginRunnerError("no such source found")
        else:
            return self.__sources

    def __setitem__(self, key, value):
        setattr(self, "_" + self.__class__.__name__ + "__" + key,
                self.resolve(value, key))

    def resolve(self, file, key):
        return ConfigurationLoader(file,
                                   self.__raw_yaml_content,
                                   key=key
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
            check_list = [
                'CheckSource',
                'CheckACL',
                'CheckRequest',
                'CheckArguments'
            ]

            def checker(x):
                checker = getattr(module, x)
                checker(query, self.__ressources,
                        self.sources(query.signature if
                                     query.signature else None,
                                     query.project,
                                     query.arguments if
                                     query.arguments else None),
                        self.__acl,
                        sha1check=self.__check_signature,
                        ipcheck=self.__check_ip)()
            list(map(checker, [method_name for method_name in dir(module) if
                               method_name in check_list]))

            return foo(self, query)

        return checks

    @check_all
    def __call__(self, query):
        data, errors = self.run_plugins(query)
        return data, errors

    def run_plugins(self, query):
        """
        Takes the query as argument and
        browses plugins to execute methods it requires.
        run_plugins is indeed excalibur's core.
        Returns obtained data and errors from all
        launched plugins.
        """

        data, errors = {}, {}
        # Load plugins
        plugin_loader = PluginLoader(self.__plugins_module)

        # Get plugins depending on the sources.yml depth
        plugins = self.plugins(query.source,
                               query.signature,
                               query.arguments,
                               query.project if
                               query.project else None,
                               )
        # Name of the function to run
        f_name = "%s_%s" % (query.ressource, query.method)

        # Actually browse plugins to launch required methods
        # First loop over registered plugins.
        for plugin_name, parameters_sets in plugins.items():
            # Load plugin
            raw_plugin_name = plugin_name
            must_replace_names = False
            # Should become the generic behavior
            if PLUGIN_NAME_SEPARATOR in plugin_name:
                must_replace_names = True
                plugin_name = plugin_name[
                    plugin_name.index(PLUGIN_NAME_SEPARATOR) + 1:]
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
                    if must_replace_names:
                        data[raw_plugin_name] = plugin_data
                    else:
                        data[plugin_name] = plugin_data

        return data, errors


class Query(object):

    """
    Queries are client requests.
    They bear data concerning both the client
    and what he requires from the api.
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
        setattr(self, "_" + self.__class__.__name__ + "__" + key,
                value)
