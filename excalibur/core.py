# -*- coding: utf-8 -*-
"""
Class to run all the process.
Excalibur's architecture is quite simple. The lib consists in
PluginRunner objects that are able to treat and react to Query
objects.
The treatments those objects make depends on their configuration
that is specified in dedicated yaml files.
"""

import collections
from functools import reduce
from importlib import import_module

from excalibur.loader import ConfigurationLoader, PluginLoader
from excalibur.check import CheckACL,\
    CheckArguments, CheckRequest, CheckSource
from excalibur.decode import DecodeArguments
from excalibur.exceptions import PluginRunnerError, WrongSignatureError
from excalibur.utils import add_args_then_encode, get_api_keys, ALL_KEYWORD,\
    PLUGIN_NAME_SEPARATOR, SOURCE_SEPARATOR, get_sources_for_all,\
    data_or_errors


from excalibur.conf import Sources


class PluginsRunner(object):

    """

    """
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

    def project_sources(self, project):
        return self.__sources[project]["sources"]

    def plugins(self, source, signature, arguments=None, project=None):
        """
        returns allowed plugins
        """
        try:
            if source != ALL_KEYWORD and SOURCE_SEPARATOR not in source:
                plugins = self.sources(signature,
                                       project,
                                       arguments)[source]
                plugins_order = plugins.get('plugins_order')

                if plugins_order:
                    # Order the plugins by the plugins_order entry in the YAML
                    # if the plugin name is in plugins_order
                    return collections.OrderedDict(sorted(
                        {k: v for k,v in plugins["plugins"].items()\
                            if k in plugins_order}.items(),
                        key=lambda x: plugins_order.index(x[0])))
                else:
                    return plugins["plugins"]
            else:
                sources = get_sources_for_all(signature,
                                              self.__sources[project],
                                              arguments,
                                              self.__check_signature)
                clean_plugin_list = {}
                for source_key, values in sources.items():
                    for key, value in values['plugins'].items():
                        clean_plugin_list[
                            source_key + PLUGIN_NAME_SEPARATOR + key] = value

                return clean_plugin_list
        except KeyError:
            raise PluginRunnerError("no such plugin found")

    def sources(self, signature, project=None, arguments=None):
        """
        Since the sources are either registered at top-level
        in the matching yml file or distibuted by projects
        sources() works as a filter to return either the whole
        yml, or the matching entries.
        """

        project = project or (
            'default' if 'default' in self.__sources.keys() else project)

        if project:
            try:
                return self.project_sources(project)
            except KeyError:
                raise PluginRunnerError("no such source found")
        else:
            return self.__sources

    def __setitem__(self, key, value):
        setattr(self, "_" + self.__class__.__name__ + "__" + key,
                self.resolve(value, key))

    def resolve(self, file_, key):
        return ConfigurationLoader(file_, self.__raw_yaml_content, key=key
                                  ).content if\
            key in ["acl", "sources", "ressources"]\
            else file_

    def sources_names(self, project=None):
        """
        Return all sources' names of a project
        """
        if project:
            try:
                return sorted(self.project_sources(project).keys())
            except KeyError:
                raise PluginRunnerError("no such source found")
        else:
            return sorted(self.__sources.keys())

    def check_all(func):
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

            def checker(method_name):
                checker = getattr(module, method_name)
                checker(query, self.__ressources,
                        self.sources(*query("checks")),
                        self.__acl,
                        sha1check=self.__check_signature,
                        ipcheck=self.__check_ip)()
            list(map(checker, [method_name for method_name in dir(module) if
                               method_name in check_list]))
            return func(self, query)

        return checks

    @check_all
    def __call__(self, query):
        data, errors = self.run(query)
        return data, errors

    def run(self, query):
        """
        Takes the query as argument and
        browses plugins to execute methods it requires.
        run is indeed excalibur's core.
        Returns obtained data and errors from all
        launched plugins.
        """
        data, errors = collections.OrderedDict(), collections.OrderedDict()
        # Load plugins
        loader = PluginLoader(self.__plugins_module)

        # Get required plugins depending on the sources.yml depth
        plugins = self.plugins(*query("plugins"))
        plugins_list = plugins.keys()

        # Actually browse plugins to launch required methods
        for name in plugins_list:
            params = plugins[name]
            (data, errors) = data_or_errors(loader, name, query,
                                            params, data, errors)
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
        exposed_attrs = ['project', 'source', 'remote_ip', 'signature',
                         'arguments', 'ressource', 'method',
                         'request_method']

        def item_to_string(k):
            return "%s:%s" % (k, str(self[k]))

        return reduce(lambda x, y: (',').join((x, y)),
                      [item_to_string(i) for i in exposed_attrs])

    def getattrsubset(self, attr_list):
        return (self[y] for y in attr_list)

    def for_(self, what):
        list_1 = ['source', 'signature', 'arguments', 'project']
        list_2 = ['signature', 'project', 'arguments']
        return {"plugins": self.getattrsubset(list_1),
                "checks": self.getattrsubset(list_2)
               }[what]

    @property
    def function_name(self):
        return "%s_%s" % (self.ressource, self.method)

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

    def __getitem__(self, key):
        return getattr(self, key) or None

    def __call__(self, for_=None):
        return self.for_(for_) if for_ in ["plugins", "checks"] else None
