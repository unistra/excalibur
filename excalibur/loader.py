# -*- coding: utf-8 -*-
"""
Class to load configuration and plugins
"""

from excalibur.exceptions import ExcaliburError, ConfigurationLoaderError, PluginLoaderError
import importlib
import yaml


class ConfigurationLoader(object):

    """
    load config from yaml
    """

    def __init__(self, file_path):
        try:
            with open(file_path, "r") as configuration_file:
                self.__content = yaml.load(configuration_file)
        except Exception:
            raise ConfigurationLoaderError(
                "error with the configuration loader: %s" % file_path)

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
