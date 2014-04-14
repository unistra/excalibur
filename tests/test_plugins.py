#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from excalibur.loader import ConfigurationLoader
from excalibur.core import PluginsRunner
from excalibur.core import Query
from excalibur.exceptions import PluginRunnerError 


class PluginsTest(TestCase):

    def setUp(self):
        # Params of the deactivate method for uds
        self.query = Query(source="etab1",
                           remote_ip="127.0.0.1",
                           signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                           arguments={"login": "testzombie1", },
                           ressource="actions",
                           method="action1",
                           request_method="GET"
                           )

        self.query2 = Query(source="etab1",
                            remote_ip="127.0.0.1",
                            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                            arguments={"login": "testzombie1", },
                            ressource="actions",
                            method="action2",
                            request_method="GET"
                            )

        # Files
        self.plugin_runner = PluginsRunner(
            "./tests/data/acl.yml", "./tests/data/sources.yml", "./tests/data/ressources.yml", "tests.plugins", self.query)

        self.data_ok = {'Plugin1': 'p1ok1', 'Plugin2': 'p2ok1'}
        self.errors_raw = {'Plugin1': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}, 'Plugin2': {
            'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}}

    def test_run_plugins(self):
        data, errors = self.plugin_runner.run_plugins()

        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})

    def test_run_plugins_error(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml", "./tests/data/sources.yml", "./tests/data/ressources.yml", "tests.plugins", self.query2)
        data, errors = plugin_runner.run_plugins()

        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})

    def test_keyerror_plugins(self):
      plugin_runner = PluginsRunner(
            "./tests/data/acl.yml", "./tests/data/sourcesnoplugins.yml", "./tests/data/ressources.yml", "tests.plugins", self.query2)
      with self.assertRaises(PluginRunnerError):
        plugin_runner.plugins

    def test_plugins_module(self):  
      self.assertEqual(self.plugin_runner.plugins_module, "tests.plugins")

    def test_query(self):
      self.assertEqual(self.query.__str__(), 
        "project:None,source:etab1,ip:127.0.0.1,\
sign:c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10,args:{'login': 'testzombie1'},\
ressource:actions,method:action1, request_method:GET")


class RunnerTest(TestCase):

    def setUp(self):

        self.query = Query(source="etab1",
                           remote_ip="127.0.0.1",
                           signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                           arguments={"login": "testzombie1", },
                           ressource="actions",
                           method="action1",
                           request_method="GET"
                           )

        self.query2 = Query(source="etab1",
                            remote_ip="127.0.0.1",
                            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                            arguments={"login": "testzombie1", },
                            ressource="actions",
                            method="action2",
                            request_method="GET"
                            )

        self.plugin_runner = PluginsRunner(
            "./tests/data/acl.yml", "./tests/data/sources.yml", "./tests/data/ressources.yml", "tests.plugins", self.query)

        self.data_ok = {'Plugin1': 'p1ok1', 'Plugin2': 'p2ok1'}
        self.errors_raw = {'Plugin1': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}, 'Plugin2': {
            'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}}

    def test_runner(self):
        data, errors = self.plugin_runner()
        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})

    def test_runner_errors(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml", "./tests/data/sources.yml", "./tests/data/ressources.yml", "tests.plugins", self.query2)
        data, errors = plugin_runner()
        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})



class RunnerWithProjectsTest(TestCase):

    def setUp(self):

        self.query = Query(source="etab1",
                           remote_ip="127.0.0.1",
                           signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                           arguments={"login": "testzombie1", },
                           ressource="actions",
                           method="action1",
                           request_method="GET",
                           project="project1"
                           )

        self.query2 = Query(source="etab1",
                            remote_ip="127.0.0.1",
                            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                            arguments={"login": "testzombie1", },
                            ressource="actions",
                            method="action2",
                            request_method="GET",
                            project="project1"
                            )

        self.plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml", "./tests/data/sources_projects.yml", "./tests/data/ressources.yml", "tests.plugins", self.query)

        self.data_ok = {'Plugin1': 'p1ok1', 'Plugin2': 'p2ok1'}
        self.errors_raw = {'Plugin1': {'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}, 'Plugin2': {
            'method': 'action2', 'source': 'etab1', 'arguments': {'login': 'testzombie1'}, 'error': 'Exception', 'ressource': 'actions', 'parameters_index': 0}}

    def test_runner(self):
        data, errors = self.plugin_runner()
        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})

    def test_runner_errors(self):

        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml", "./tests/data/sources_projects.yml", "./tests/data/ressources.yml", "tests.plugins", self.query2)
        data, errors = plugin_runner()
        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})


if __name__ == '__main__':
    main()
