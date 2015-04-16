# -*- coding: utf-8 -*-
"""
Class to run all the process.
Excalibur's architecture is quite simple. The lib consists in
PluginRunner objects that are able to treat and react to Query
objects.
The treatments those objects make depends on their configuration
that is specified in dedicated yaml files.
"""

from excalibur.loader import ConfigurationLoader, PluginLoader

from excalibur.exceptions import PluginRunnerError

from functools import reduce as red
from excalibur.utils import ALL_KEYWORD,\
    PLUGIN_NAME_SEPARATOR, SOURCE_SEPARATOR, get_sources_for_all,\
    data_or_errors, check_all


class PluginsRunner(object):

    """
    The main class of the application.
    """
    # 22/04/2014 :checksign defaults to false

    def __init__(self, acl, sources, ressources,
                 plugins_module, check_signature=True, check_ip=True,
                 raw_yaml_content=False,
                 http_sig=False):
        self.__raw_yaml_content = raw_yaml_content
        self["acl"] = acl
        self["sources"] = sources
        self["ressources"] = ressources
        self["plugins_module"] = plugins_module
        self["check_signature"] = check_signature
        self["check_ip"] = check_ip
        self["http_sig"] = http_sig

    @property
    def acl(self):
        """
        ACL getter
        """
        return self["acl"]

    @property
    def ressources(self):
        """
        ressources getter
        """
        return self['ressources']

    @property
    def plugins_module(self):
        """
        getter for the plugin module
        """
        return self['plugins_module']

    def project_sources(self, project):
        """
        method to get soources in project
        """
        return self['sources'][project]["sources"]

    def plugins(self, source, signature=None,
                arguments=None, project="default"):
        """
        returns allowed plugins
        """
        try:
            if source != ALL_KEYWORD and SOURCE_SEPARATOR not in source:
                return self.sources(project,
                                    arguments)[source]["plugins"]
            else:
                sources = get_sources_for_all(signature,
                                              self['sources'][project],
                                              arguments,
                                              self['check_signature'])
                clean_plugin_list = {}
                for key, value in sources.items():
                    for clef, valeur in value['plugins'].items():
                        clean_plugin_list[
                            key + PLUGIN_NAME_SEPARATOR + clef] = valeur
                return clean_plugin_list
        except KeyError:
            raise PluginRunnerError("no such plugin found")

    def sources(self, project=None, arguments=None, headers=None):
        """
        Since the sources are either registered at top-level
        in the matching yml file or distibuted by projects
        sources() works as a filter to return either the whole
        yml, or the matching entries.
        """
        try:
            return self.project_sources(project)
        except KeyError:
            raise PluginRunnerError("no such source found")

    def __setitem__(self, key, value):
        """
        setitem is overriden so that in the init, the function resolve
        can be called for each argument received in the constructor.
        """
        setattr(self, "_" + self.__class__.__name__ + "__" + key,
                self.resolve(value, key))

    def __getitem__(self, key):
        """
        """
        ret = None
        try:
            ret = getattr(self, "_" + self.__class__.__name__ + "__" + key)
        except AttributeError:
            raise KeyError()
        return ret

    def resolve(self, conf_file, key):
        """
        load files or put strings
        """
        return ConfigurationLoader(conf_file, key,
                                   self.__raw_yaml_content,
                                   key=key).content if\
            key in ["acl", "sources", "ressources"]\
            else conf_file

    def sources_names(self, project="default"):
        """
        Return all sources' names of a project
        """
        try:
            return sorted(self.project_sources(project).keys())
        except KeyError:
            raise PluginRunnerError("no such source found")

    @check_all
    def __call__(self, query):
        """
        main execution
        """
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
        data, errors = {}, {}
        # Load plugins
        loader = PluginLoader(self['plugins_module'])
        # Get required plugins depending on the sources.yml depth
        plugins = self.plugins(*query("plugins"))
        # Actually browse plugins to launch required methods
        for name, params in plugins.items():
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
                 project="default",
                 arguments=None,
                 headers=None):

        self["project"] = project
        self["source"] = source
        self["remote_ip"] = remote_ip
        self["signature"] = signature
        self["arguments"] = arguments if arguments else {}
        self["ressource"] = ressource
        self["method"] = method
        self["request_method"] = request_method
        self["headers"] = headers

    def __str__(self):
        """
        string representation
        """
        exposed_attrs = ['project', 'source', 'remote_ip', 'signature',
                         'arguments', 'ressource', 'method',
                         'request_method']

        def item_to_string(k):
            """
            k,v pair in a string
            """
            return "%s:%s" % (k, str(self[k]))

        return red(lambda x, y: (',').join((x, y)),
                   [item_to_string(i) for i in exposed_attrs])

    def getattrsubset(self, attrlist):
        """
        return self[something] for something in a list
        """
        return (self[y] for y in attrlist)

    def for_(self, what):
        """
        return the list of attrs required in  a context
        """
        plugins = ['source', 'signature', 'arguments', 'project']
        checks = ['project', 'arguments', 'headers']
        return {"plugins": self.getattrsubset(plugins),
                "checks": self.getattrsubset(checks)}[what]

    @property
    def function_name(self):
        """
        returns the name of the function
        """
        return "%s_%s" % (self.ressource, self.method)

    @property
    def project(self):
        """
        project getter
        """
        return self['project']

    @property
    def source(self):
        """
        source getter
        """
        return self['source']

    @property
    def remote_ip(self):
        """
        remote_ip getter
        """
        return self['remote_ip']

    @property
    def signature(self):
        """
        signature getter
        """
        return self['signature']

    @property
    def arguments(self):
        """
        arguments getter
        """
        return self['arguments']

    @property
    def headers(self):
        """
        headers getter
        """
        return self['headers']

    @property
    def ressource(self):
        """
        ressource getter
        """
        return self['ressource']

    @property
    def method(self):
        """
        method getter
        """
        return self['method']

    @property
    def request_method(self):
        """
        request_method getter
        """
        return self['request_method']

    def __setitem__(self, key, value):
        """
        item setter
        """
        setattr(self, "_" + self.__class__.__name__ + "__" + key,
                value)

    def __getitem__(self, key):
        """
        """
        ret = None
        try:
            ret = getattr(self, "_" + self.__class__.__name__ + "__" + key)
        except AttributeError:
            raise KeyError()
        return ret

    def __call__(self, for_=None):
        """
        call
        """
        return self.for_(for_) if for_ in ["plugins", "checks"] else None
