#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from excalibur.utils import run_plugins
from excalibur.loader import ConfigurationLoader
from excalibur.core import PluginsRunner
from excalibur.core import Query


class PluginsTest(TestCase):

    def setUp(self):
        #Params of the deactivate method for uds
        self.query = Query( source= "etab1",
              remote_ip = "127.0.0.1",
              signature = "c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
              arguments = { "login": "testzombie1", },
              ressource = "actions",
              method = "action1",
              request_method = "GET"
            )
        
        self.query2 = Query( source= "etab1",
              remote_ip = "127.0.0.1",
              signature = "c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
              arguments = { "login": "testzombie1", },
              ressource = "actions",
              method = "action2",
              request_method = "GET"
            )

        #Files
        self.plugin_runner = PluginsRunner("./data/acl.yml", "./data/sources.yml", "./data/ressources.yml", "tests.plugins", self.query)

        self.data_ok = {'Plugin1': 'p1ok1', 'Plugin2': 'p2ok1'}
        self.errors_raw = {'Plugin1': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}, 'Plugin2': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}}


    def test_run_plugins(self):
        plugins = self.plugin_runner.sources[self.plugin_runner.query.source]["plugins"]
        data, errors = self.plugin_runner.run_plugins(plugins)

        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})


    def test_run_plugins_error(self):
        plugin_runner = PluginsRunner("./data/acl.yml", "./data/sources.yml", "./data/ressources.yml", "tests.plugins", self.query2)
        plugins = plugin_runner.sources[plugin_runner.query.source]["plugins"]
        data, errors = plugin_runner.run_plugins(plugins)
 
        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})
 
 
class RunnerTest(TestCase):
  
    def setUp(self):
  
        self.query = Query( source= "etab1",
              remote_ip = "127.0.0.1",
              signature = "c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
              arguments = { "login": "testzombie1", },
              ressource = "actions",
              method = "action1",
              request_method = "GET"
            )
          
        self.query2 = Query( source= "etab1",
              remote_ip = "127.0.0.1",
              signature = "c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
              arguments = { "login": "testzombie1", },
              ressource = "actions",
              method = "action2",
              request_method = "GET"
            )
          
        self.plugin_runner = PluginsRunner("./data/acl.yml", "./data/sources.yml", "./data/ressources.yml", "tests.plugins", self.query)
  
        self.data_ok = {'Plugin1': 'p1ok1', 'Plugin2': 'p2ok1'}
        self.errors_raw = {'Plugin1': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}, 'Plugin2': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}}
  
  
  
    def test_runner(self):
        data, errors = self.plugin_runner()
        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})
  
  
    def test_runner_errors(self):
  
        plugin_runner = PluginsRunner("./data/acl.yml", "./data/sources.yml", "./data/ressources.yml", "tests.plugins", self.query2)
        data, errors = plugin_runner()
        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})


if __name__ == '__main__':
    main()
