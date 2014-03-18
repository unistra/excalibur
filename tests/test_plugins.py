#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from excalibur.utils import run_plugins
from excalibur.loader import ConfigurationLoader
from excalibur.runner import PluginsRunner

class PluginsTest(TestCase):

    def setUp(self):
        #Params of the deactivate method for uds
        self.source = "etab1"
        self.remote_ip = "127.0.0.1"
        self.signature = "c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10"
        self.arguments = { "login": "testzombie1", }
        self.ressource = "actions"
        self.method = "action1"
        self.request_method = "GET"

        #Files
        self.acl = ConfigurationLoader("./data/acl.yml").content
        self.sources = ConfigurationLoader("./data/sources.yml").content
        self.ressources = ConfigurationLoader("./data/ressources.yml").content

        self.plugin_module = "tests.plugins"

        self.data_ok = {'Plugin1': 'p1ok1', 'Plugin2': 'p2ok1'}
        self.errors_raw = {'Plugin1': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}, 'Plugin2': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}}


    def test_run_plugins(self):
        data, errors = run_plugins(self.sources[self.source]["plugins"], self.ressource, self.method, 
            self.arguments, self.source, self.plugin_module)

        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})


    def test_run_plugins_error(self):
        self.method = "action2"
        data, errors = run_plugins(self.sources[self.source]["plugins"], self.ressource, self.method, 
            self.arguments, self.source, self.plugin_module)

        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})


class RunnerTest(TestCase):

    def setUp(self):

        self.query = { 'source': "etab1",
                  'remote_ip' : "127.0.0.1",
                  'signature' : "c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                  'arguments' : { "login": "testzombie1", },
                  'ressource' : "actions",
                  'method' : "action1",
                  'request_method' : "GET"
                }

        self.acl_path = "./data/acl.yml"
        self.sources_path = "./data/sources.yml"
        self.ressources_path = "./data/ressources.yml"
        self.plugin_module = "tests.plugins"

        self.data_ok = {'Plugin1': 'p1ok1', 'Plugin2': 'p2ok1'}
        self.errors_raw = {'Plugin1': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}, 'Plugin2': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}}



    def test_runner(self):
        plugins_runner = PluginsRunner(self.acl_path, self.sources_path, self.ressources_path, self.plugin_module, self.query)
        data, errors = plugins_runner()
        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})


    def test_runner_errors(self):
        self.query['method'] = "action2"
        plugins_runner = PluginsRunner(self.acl_path, self.sources_path, self.ressources_path, self.plugin_module, self.query)
        data, errors = plugins_runner()
        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})


if __name__ == '__main__':
    main()
