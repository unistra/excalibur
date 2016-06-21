#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from excalibur.loader import ConfigurationLoader
from excalibur.core import PluginsRunner
from excalibur.core import Query
from excalibur.exceptions import PluginRunnerError
from excalibur.exceptions import IPNotAuthorizedError,WrongSignatureError
from excalibur.utils import ALL_KEYWORD
import yaml


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
            "./tests/data/acl.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")

        self.data_ok = {'Plugin1': 'p1ok1', 'Plugin2': 'p2ok1'}
        self.errors_raw = {'Plugin1': {
                            'error_message': 'error plugin 1 action 2 !',
                            'method': 'action2',
                            'source': 'etab1',
                            'arguments': {'login': 'testzombie1'},
                            'error': 'Exception',
                            'ressource': 'actions',
                            'parameters_index': 0,
                            'project': None},
                           'Plugin2': {
                            'error_message': 'error plugin 2 action 2 !',
                            'method': 'action2',
                            'source': 'etab1',
                            'arguments': {'login': 'testzombie1'},
                            'error': 'Exception', 'ressource':
                            'actions',
                            'parameters_index': 0,
                            'project': None},
                           }

    def test_run(self):
        data, errors = self.plugin_runner.run(self.query)

        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})

    def test_run_error(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")
        data, errors = plugin_runner.run(self.query2)

        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})

    def test_keyerror_plugins(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sourcesnoplugins.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")
        with self.assertRaises(PluginRunnerError):
            plugin_runner.plugins(self.query.source, self.query.project)

    def test_plugins_module(self):
        self.assertEqual(self.plugin_runner.plugins_module, "tests.plugins")

    def test_query(self):
        self.assertEqual(self.query.__str__(),
                         "project:None,source:etab1,remote_ip:127.0.0.1,\
signature:c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10,arguments:{'login': 'testzombie1'},\
ressource:actions,method:action1,request_method:GET")


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

        self.query3 = Query(source="etab2",
                            remote_ip="127.0.0.1",
                            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                            arguments={"login": "testzombie1", },
                            ressource="actions",
                            method="action1",
                            request_method="GET"
                            )

        self.query4 = Query(source="etab3",
                            remote_ip="127.0.0.1",
                            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                            arguments={"login": "testzombie1", },
                            ressource="actions",
                            method="action1",
                            request_method="GET"
                            )

        self.plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")

        self.data_ok = {'Plugin1': 'p1ok1', 'Plugin2': 'p2ok1'}
        self.errors_raw = {'Plugin1': {
                            'method': 'action2',
                            'source': 'etab1',
                            'arguments': {'login': 'testzombie1'},
                            'error': 'Exception',
                            'error_message': 'error plugin 1 action 2 !',
                            'ressource': 'actions',
                            'parameters_index': 0,
                            'project': None},
                           'Plugin2': {
                            'method': 'action2',
                            'source': 'etab1',
                            'arguments': {'login': 'testzombie1'},
                            'error': 'Exception',
                            'error_message': 'error plugin 2 action 2 !',
                            'ressource': 'actions',
                            'parameters_index': 0,
                            'project': None}
                           }
        self.raw_acl = """
etab1:
    actions:
        - action1
        - action2

etab2:
    actions:
        - action1

"""
        self.raw_sources = """
etab1:
    apikey: S3CR3T
    ip:
            - 127.0.0.1
    plugins:

        Plugin1:

            -   spore: S3CR3T
                token: S3CR3T
        Plugin2:
            -   spore: S3CR3T
                token: S3CR3T

        Plugin3:
            -   spore: S3CR3T
                token: S3CR3T

etab2:
    apikey: S3CR3T2
    ip:
            - 127.0.0.1
    plugins:

        Plugin1:

            -   spore: S3CR3T2
                token: S3CR3T2
        Plugin2:
            -   spore: S3CR3T2
                token: S3CR3T2
"""
        self.raw_ressources = """
actions:
    action1:
        request method: GET
        arguments:
            login:
                checks:
                    min length: 2
                    max length: 50

    action2:
        request method: GET
        arguments:
            login:
                checks:
                    min length: 2
                    max length: 50
"""

    def test_runner(self):
        data, errors = self.plugin_runner(self.query)
        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})

    def test_runner_errors(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")
        data, errors = plugin_runner(self.query2)
        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})

    def test_sources_names(self):
        self.assertEqual(
            self.plugin_runner.sources_names(), ['etab1', 'etab2'])

    def test_runner_with_raw_yaml(self):
        plugin_runner = PluginsRunner(
            self.raw_acl,
            self.raw_sources,
            self.raw_ressources,
            "tests.plugins",
            raw_yaml_content=True)

        data, errors = plugin_runner(self.query)
        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})

    def test_runner_with_raw_yaml_errors(self):
        plugin_runner = PluginsRunner(
            self.raw_acl,
            self.raw_sources,
            self.raw_ressources,
            "tests.plugins",
            raw_yaml_content=True)

        data, errors = plugin_runner(self.query2)
        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})

    def test_runner_with_plugins_order(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources_with_plugins_order.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        data, errors = plugin_runner(self.query)
        self.assertListEqual(['Plugin2', 'Plugin1'], list(data.keys()))

    def test_runner_with_plugins_order_and_more_plugins(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources_with_plugins_order.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        data, errors = plugin_runner(self.query3)
        self.assertListEqual(['Plugin2'], list(data.keys()))

    def test_runner_with_plugins_order_and_less_plugins(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources_with_plugins_order.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        data, errors = plugin_runner(self.query4)
        self.assertListEqual(['Plugin2', 'Plugin1'], list(data.keys()))


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

        self.query3 = Query(source=ALL_KEYWORD,
                            remote_ip="127.0.0.1",
                            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                            arguments={"login": "testzombie1", },
                            ressource="actions",
                            method="action1",
                            request_method="GET",
                            project="project1"
                            )

        self.query4 = Query(source="etab1,etab2",
                            remote_ip="127.0.0.1",
                            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                            arguments={"login": "testzombie1", },
                            ressource="actions",
                            method="action1",
                            request_method="GET",
                            project="project1"
                            )

        self.query5 = Query(source="etab2",
                            remote_ip="127.0.0.1",
                            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                            arguments={"login": "testzombie1", },
                            ressource="actions",
                            method="action1",
                            request_method="GET",
                            project="project1"
                            )

        self.query6 = Query(source="etab3",
                            remote_ip="127.0.0.1",
                            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                            arguments={"login": "testzombie1", },
                            ressource="actions",
                            method="action1",
                            request_method="GET",
                            project="project1"
                            )

        self.plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/sources_projects.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")

        self.plugin_runner2 = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/query4_project.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")

        self.data_ok = {'Plugin1': 'p1ok1', 'Plugin2': 'p2ok1'}
        self.errors_raw = {'Plugin1': {
                            'method': 'action2',
                            'source': 'etab1',
                            'arguments': {'login': 'testzombie1'},
                            'error': 'Exception',
                            'error_message': 'error plugin 1 action 2 !',
                            'ressource': 'actions',
                            'parameters_index': 0,
                            'project': 'project1'},
                           'Plugin2': {
                            'method': 'action2',
                            'source': 'etab1',
                            'arguments': {'login': 'testzombie1'},
                            'error': 'Exception',
                            'error_message': 'error plugin 2 action 2 !',
                            'ressource': 'actions',
                            'parameters_index': 0,
                            'project': 'project1'}}

        self.raw_acl = """
project1:
    etab1:
        actions:
            - action1
            - action2

    etab2:
        actions:
            - action1

project2:
    etab1:
        actions:
            - action1
            - action2

"""
        self.raw_sources = """
project1:
     sources:
        etab1:
            apikey: S3CR3T
            ip:
                    - 127.0.0.1
            plugins:

                Plugin1:

                    -   spore: S3CR3T
                        token: S3CR3T
                Plugin2:
                    -   spore: S3CR3T
                        token: S3CR3T

        etab2:
            apikey: S3CR3T2
            ip:
                    - 127.0.0.1
            plugins:

                Plugin1:

                    -   spore: S3CR3T2
                        token: S3CR3T2
                Plugin2:
                    -   spore: S3CR3T2
                        token: S3CR3T2


project2:
    sources:
        etab1:
            apikey: S3CR3T
            ip:
                    - 127.0.0.1
            plugins:

                Plugin1:

                    -   spore: S3CR3T
                        token: S3CR3T
                Plugin2:
                    -   spore: S3CR3T
                        token: S3CR3T
"""
        self.raw_ressources = """
actions:
    action1:
        request method: GET
        arguments:
            login:
                checks:
                    min length: 2
                    max length: 50

    action2:
        request method: GET
        arguments:
            login:
                checks:
                    min length: 2
                    max length: 50
"""

    def test_runner(self):
        data, errors = self.plugin_runner(self.query)
        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})

    def test_runner_query4_one_requested_source_does_not_match(self):
        with self.assertRaises(WrongSignatureError):
            data, errors = self.plugin_runner(self.query4)

    def test_runner_query4_one_requested_source(self):
        """
        """
        data, errors = self.plugin_runner2(self.query4)
        self.assertTrue(data["etab2|Plugin2"]=="p2ok1" and data["etab1|Plugin1"]=="p1ok1" and data["etab1|Plugin2"]=='p2ok1')

    def test_runner_errors(self):

        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/sources_projects_encoded_api_keys.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")
        data, errors = plugin_runner(self.query2)
        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})

    def test_runner_with_query_source_set_to_all(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/sources_projects_encoded_api_keys.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")
        data, errors = plugin_runner(self.query3)
        self.assertTrue(data["etab1|Plugin1"]=="p1ok1" and data["etab1|Plugin2"]=='p2ok1')
        self.assertTrue("etab2|Plugin2" not in data)

    def test_query_source_set_to_all_and_multiple_etabs(self):
        """
        Checks that with 'source==all', data are correctly returned from
        multiple establishments 
        """
        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/source_set_to_all_and_multiple_etabs.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")
        data, errors = plugin_runner(self.query3)
        self.assertTrue(data["etab2|Plugin2"]=="p2ok1" and data["etab1|Plugin1"]=="p1ok1")

    def test_request_set_to_all_and_checksignature_set_to_false(self):
        """
        """
        plugin_runner = PluginsRunner(
            "./tests/data/acl_three_etabs.yml",
            "./tests/data/source_set_to_all_multiple_etabs_one_missing_api_key.yml",
            "./tests/data/ressources.yml",
            "tests.plugins",
            check_signature=False
            )
        data, errors = plugin_runner(self.query3)
        self.assertTrue(data["etab2|Plugin2"]=="p2ok1" and data["etab1|Plugin1"]=="p1ok1")

    def test_query_source_set_to_all__multiple_etabs_multiple_ips(self):
        """
        """
        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/sources_many_ip.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")
        data, errors = plugin_runner(self.query3)
        self.assertTrue(data["etab2|Plugin2"]=="p2ok1" and data["etab1|Plugin1"]=="p1ok1")
        self.assertTrue("etab3|Plugin2" not in data)

    def test_query_all_missing_ip_in_an_etab(self):
        """
        """
        plugin_runner = PluginsRunner(
        "./tests/data/acl_projects.yml",
        "./tests/data/sources_all_with_apikey_matching_but_ip_not_authorized.yml",
        "./tests/data/ressources.yml",
        "tests.plugins")

        with self.assertRaises(IPNotAuthorizedError):
            data, errors = plugin_runner(self.query3)

#         self.assertTrue(data["Plugin2"]=="p2ok1" and data["Plugin1"]=="p1ok1")

    def test_query_source_set_to_all_and_multiple_etabs_with_errors(self):
        """
        Checks that with 'source==all', but ip does not match
        errors are raised
        NEEDS IP_CHECK TO BE REENABLED
        """
        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/source_set_to_all_and_multiple_etabs.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")
        data, errors = plugin_runner(self.query3)

#         self.assertTrue(data["Plugin2"]=="p2ok1" and data["Plugin1"]=="p1ok1")

    def test_sources_names(self):
        self.assertEqual(self.plugin_runner.sources_names(self.query.project),
                         ['etab1', 'etab2'])
        self.assertEqual(self.plugin_runner.sources_names("project2"),
                         ['etab1'])

    def test_failing_sources_names(self):
        p = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/sourcesnoplugins.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")
        with self.assertRaises(PluginRunnerError):
            p.sources_names(self.query.project)

    def test_runner_with_raw_yaml(self):
        plugin_runner = PluginsRunner(
            self.raw_acl,
            self.raw_sources,
            self.raw_ressources,
            "tests.plugins",
            raw_yaml_content=True)

        data, errors = plugin_runner(self.query)
        self.assertEqual(data, self.data_ok)
        self.assertEqual(errors, {})

    def test_runner_with_raw_yaml_errors(self):
        plugin_runner = PluginsRunner(
            self.raw_acl,
            self.raw_sources,
            self.raw_ressources,
            "tests.plugins",
            raw_yaml_content=True)

        data, errors = plugin_runner(self.query2)
        self.assertEqual(errors, self.errors_raw)
        self.assertEqual(data, {})

    def test_runner_projects_with_plugins_order(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/sources_projects_with_plugins_order.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        data, errors = plugin_runner(self.query)
        self.assertListEqual(['Plugin2', 'Plugin1'], list(data.keys()))

    def test_runner_projects_with_plugins_order_and_more_plugins(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/sources_projects_with_plugins_order.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        data, errors = plugin_runner(self.query5)
        self.assertListEqual(['Plugin2'], list(data.keys()))

    def test_runner_projects_with_plugins_order_and_less_plugins(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/sources_projects_with_plugins_order.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        data, errors = plugin_runner(self.query6)
        self.assertListEqual(['Plugin2', 'Plugin1'], list(data.keys()))


if __name__ == '__main__':
    main()
