#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from excalibur.loader import ConfigurationLoader, PluginLoader
from excalibur.exceptions import ConfigurationLoaderError, PluginLoaderError
from tests.plugins.Plugin1 import Plugin1
from tests.plugins.Plugin2 import Plugin2


class ConfigurationLoaderTest(TestCase):
    """ 
    test with files
    """

    def setUp(self):
        self.file_path_ok = "./tests/data/sources.yml"
        self.file_path_wrong = "/tmp/doesntexist"
        self.raw = {'etab2': {'ip': ['127.0.0.1'], 'apikey': 'S3CR3T2', 
            'plugins': {'Plugin1': [{'spore': 'S3CR3T2', 'token': 'S3CR3T2'}], 
            'Plugin2': [{'spore': 'S3CR3T2', 'token': 'S3CR3T2'}]}}, 'etab1': 
            {'ip': ['127.0.0.1'], 'apikey': 'S3CR3T', 'plugins': {'Plugin1': 
            [{'spore': 'S3CR3T', 'token': 'S3CR3T'}], 'Plugin2': 
            [{'spore': 'S3CR3T', 'token': 'S3CR3T'}], 'Plugin3': 
            [{'spore': 'S3CR3T', 'token': 'S3CR3T'}]}}}
        self.raw_wrong = {'error': 'error'}

    def test_load_content_ok(self):
        c = ConfigurationLoader(self.file_path_ok)
        self.assertEqual(c.content, self.raw)

    def test_load_content_wrong(self):
        c = ConfigurationLoader(self.file_path_ok)
        self.assertNotEqual(c.content, self.raw_wrong)

    def test_load_content_doesntexist(self):
        with self.assertRaises(ConfigurationLoaderError):
            ConfigurationLoader(self.file_path_wrong)


class ConfigurationLoaderRawTest(TestCase):
    """
    test with raw content
    """

    def setUp(self):
        self.content_ok = "test: ['salut','hello']"
        self.content_wrong = "test:\t['salut','hello']"
        self.raw = {'test': ['salut', 'hello']}
        self.raw_wrong = {'error': 'error'}

    def test_load_content_ok(self):
        c = ConfigurationLoader(self.content_ok, raw_yaml_content=True)
        self.assertEqual(c.content, self.raw)

    def test_load_content_wrong(self):
        c = ConfigurationLoader(self.content_ok, raw_yaml_content=True)
        self.assertNotEqual(c.content, self.raw_wrong)

    def test_load_content_doesntexist(self):
        with self.assertRaises(ConfigurationLoaderError):
            ConfigurationLoader(self.content_wrong, raw_yaml_content=True)


class PluginLoaderTest(TestCase):

    def setUp(self):
        self.plugin_module = "tests.plugins"
        self.plugin1 = "Plugin1"
        self.plugin_doesntexist = "NotExist"
        self.plugin_wrong = "Plugin2"

    def test_load_plugin_ok(self):
        p = PluginLoader(self.plugin_module)
        instance = p.get_plugin(self.plugin1)
        self.assertIsInstance(instance, Plugin1)

    def test_load_plugin_wrong(self):
        p = PluginLoader(self.plugin_module)
        instance = p.get_plugin(self.plugin1)
        self.assertNotIsInstance(instance, Plugin2)

    def test_load_plugin_doesntexist(self):
        with self.assertRaises(PluginLoaderError):
            p = PluginLoader(self.plugin_doesntexist)
            instance = p.get_plugin(self.plugin1)


if __name__ == '__main__':
    main()
