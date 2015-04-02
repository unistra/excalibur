# -*- coding: utf-8 -*-
"""
Class to load configuration and plugins
"""

from excalibur.exceptions import ExcaliburError, ConfigurationLoaderError,\
    PluginLoaderError, SourcesNotParsable
    
import importlib
import yaml


class ConfigurationLoader(object):

    """
    load config from yaml
    """

    def __init__(self, myyaml, what, raw_yaml_content=False, key=None):
        """
        Load yaml file, or raw yaml if raw_yaml_content is True
        """
        prefix = ""
        if key:
            prefix = """!!python/object:excalibur.conf.""" + key.title() + """
"""

        try:
            if not raw_yaml_content:
                with open(myyaml, "r") as configuration_file:
                    self.__content = yaml.load(
                        prefix + configuration_file.read())
            else:
                self.__content = yaml.load(prefix + myyaml)

            if self.__content and what == "sources":
                def check_values(x):
                    if type(x) is dict:
                        if "sources" not in x.keys():
                            raise SourcesNotParsable("one of the configured projects misses the 'sources' entry")
                    else:
                        raise SourcesNotParsable("the structure of the yaml is wrong")

                list([check_values(x) for x in self.__content.values()])

        except Exception as e:
            if type(e) is SourcesNotParsable:
                raise e
            else:
                raise ConfigurationLoaderError(
                    "error with the configuration loader: %s, %s" % (myyaml, e))

    @property
    def content(self):
        """
        Return configuration content.
        """
        return self.__content


class PluginLoader(object):

    """
    Create plugin instance
    """

    def __init__(self, plugin_module):
        self.plugin_module = plugin_module

    def get_plugin(self, plugin_name):
        """
        return plugin instance
        """
        try:
            module = importlib.import_module(
                "%s.%s" % (self.plugin_module, plugin_name))
            plugin = getattr(module, plugin_name)
            return plugin()
        except Exception as e:
            raise PluginLoaderError(
                "Plugin %s failed to load: %s" % (plugin_name, e))
    
