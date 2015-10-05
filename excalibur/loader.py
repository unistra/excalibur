# -*- coding: utf-8 -*-
"""
Class to load configuration and plugins
"""

from excalibur.exceptions import ExcaliburError, ConfigurationLoaderError,\
    PluginLoaderError
import importlib
import yaml
from excalibur.utils import PLUGIN_NAME_SEPARATOR, separator_contained


class ConfigurationLoader(object):

    """
    load config from yaml
    """

    def __init__(self, myyaml, raw_yaml_content=False, key=None):
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
        except Exception as e:
            raise ConfigurationLoaderError(
                "error with the configuration loader: %s" % myyaml)

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

    def __init__(self, plugin_module, query=None):
        self.plugin_module = plugin_module
        self.query = query

    def clean_plugin_name(self, plugin_name):
        return plugin_name[plugin_name.index(PLUGIN_NAME_SEPARATOR) + 1:]

    def set_plugin_name(self, plugin_name):
        return self.clean_plugin_name(plugin_name) if\
            separator_contained(plugin_name) else plugin_name

    def get_plugin(self, plugin_name):
        """
        return plugin instance
        """
        try:
            cleaned_name = self.set_plugin_name(plugin_name)
            module = importlib.import_module(
                "%s.%s" % (self.plugin_module, cleaned_name))
            plugin = getattr(module, cleaned_name)
            return plugin(query=self.query, name=cleaned_name, original_name=plugin_name)
        except Exception as e:
            raise PluginLoaderError(
                "Plugin %s failed to load: %s" % (plugin_name, e))
