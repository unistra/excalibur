#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from excalibur.decode import DecodeArguments
from excalibur.loader import ConfigurationLoader
from excalibur.check import CheckSource, CheckACL, CheckRequest, \
    CheckArguments, Check
from excalibur.exceptions import SourceNotFoundError, IPNotAuthorizedError,\
    WrongSignatureError, NoACLMatchedError, RessourceNotFoundError,\
    MethodNotFoundError, HTTPMethodError, ArgumentError, \
    ArgumentCheckMethodNotFoundError, ExcaliburError, \
    DecodeAlgorithmNotFoundError
from excalibur.core import PluginsRunner, Query
import base64
from importlib import import_module
from excalibur.utils import ALL_KEYWORD


class CheckTest(TestCase):

    """
    Unit test for check method
    Warning : "Params" of the setUp method need to be valid with
    your yaml files
    """

    def setUp(self):
        # Params of the deactivate method for uds
        self.query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GET"
        )

        self.query2 = Query(
            source="etab1",
            remote_ip="9.9.9.9",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GET"
        )
        encodedzombie = base64.b64encode(b"testzombie1")
        self.query3 = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            arguments={"login": encodedzombie, },
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            ressource="actions",
            method="action1",
            request_method="GET")
        # Files
        self.plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressources.yml",
            "tests.plugins",)

    """
    Check Source
    """

    def test_check_source(self):
        """ test check sources """
        try:
            CheckSource(
                self.query, None,
                self.plugin_runner.sources(self.query.project), None)()

        except:
            self.fail("Error check source")

    def test_check_source_not_found(self):
        """ test check sources """
        query1 = Query(
            source="etabnull",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GET"
        )
        with self.assertRaises(SourceNotFoundError):
            CheckSource(query1,
                        None,
                        self.plugin_runner.sources(query1.project), None)()

    def test_check_source_ip_not_authorized(self):
        """ test check sources """
        with self.assertRaises(IPNotAuthorizedError):
            CheckSource(
                self.query2,
                None,
                self.plugin_runner.sources(self.query2.project), None)()

    def test_check_source_ip_with_regexp(self):
        plugin_runner2 = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sourcesipregexp.yml",
            "./tests/data/ressources.yml",
            "tests.plugins")
        try:
            CheckSource(
                self.query2, None,
                plugin_runner2.sources(self.query2.project), None)()
        except:
            self.fail("Error test_check_source_ip_with_regexp")

    def test_check_source_signature_error(self):
        """ test check sources """
        query3 = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="ERROR",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GET"
        )

        with self.assertRaises(WrongSignatureError):
            CheckSource(
                query3,
                None,
                self.plugin_runner.sources(query3.project),
                None)()
    """
    Check ACL
    """

    def test_check_acl(self):
        """ test check acl """
        try:
            CheckACL(self.query, None, None, self.plugin_runner.acl)()
        except Exception as e:
            self.fail("Error check acl")

    def test_check_acl_no_matched(self):
        """ test check acl """
        query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="actionull",
            request_method="GET"
        )
        with self.assertRaises(NoACLMatchedError):
            CheckACL(query, None, None, self.plugin_runner.acl)()

        query2 = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GET",
            project="keyerror"
        )
        with self.assertRaises(NoACLMatchedError):
            CheckACL(query2, None, None, self.plugin_runner.acl)()

        query3 = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="wrongmethod",
            request_method="GET",
            project="project1"
        )
        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressources.yml",
            "tests.plugins",
            query3)

        with self.assertRaises(NoACLMatchedError):
            CheckACL(query3, None, None, plugin_runner.acl)()

    """
    Check Request
    """

    def test_check_request(self):
        """ test check request """
        try:
            CheckRequest(
                self.query, self.plugin_runner.ressources, None, None)()
        except:
            self.fail("error check request")

    def test_check_request_ressource_not_found(self):
        """ test check request """
        query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="ressourcenull",
            method="action1",
            request_method="GET"
        )
        with self.assertRaises(RessourceNotFoundError):
            CheckRequest(query, self.plugin_runner.ressources, None, None)()

    def test_check_request_method_not_found(self):
        """ test check request """
        query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="methodnull",
            request_method="GET"
        )
        with self.assertRaises(MethodNotFoundError):
            CheckRequest(query, self.plugin_runner.ressources, None, None)()

    def test_check_request_method_not_specified(self):
        """ test check request """
        error = None
        query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="POST"
        )
        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressourcewithoutrequestmethod.yml",
            "tests.plugins",
            query)
        try:
            CheckRequest(query, plugin_runner.ressources, None, None)()
        except Exception as e:
            error = e
        self.assertTrue(not error)

    def test_check_request_method_http_error(self):
        """ test check request """
        query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GETnull"
        )
        with self.assertRaises(HTTPMethodError):
            CheckRequest(query, self.plugin_runner.ressources, None, None)()

    def test_check_request_args_error(self):
        """ test check request """
        query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments="argumentsnull",
            ressource="actions",
            method="action1",
            request_method="GET"
        )
        query2 = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments="argumentsnull",
            ressource="actions",
            method="action2",
            request_method="GET"
        )
        with self.assertRaises(ArgumentError):
            CheckRequest(query, self.plugin_runner.ressources, None, None)()
# Not required anymore, when there is no arguments entry,
# no checks are made
#         plugin_runner = PluginsRunner(
#             "./tests/data/acl.yml",
#             "./tests/data/sources.yml",
#             "./tests/data/ressourceswrongcheck.yml",
#             "tests.plugins",
#             self.query)
#
#         with self.assertRaises(ArgumentError):
#             CheckRequest(query2,plugin_runner.ressources)()

    """
    Check arguments
    """

    def test_check_arguments(self):
        """ test check arguments """
        try:
#             DecodeArguments(self.query,
#                             self.plugin_runner.ressources)()
            CheckArguments(
                self.query, self.plugin_runner.ressources, None, None)()

        except:
            self.fail("error check arguments")

    def test_check_arguments_error(self):
        """ test check arguments """

        query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "a", },
            ressource="actions",
            method="action1",
            request_method="GET"
        )
        with self.assertRaises(ArgumentError):
#             DecodeArguments(self.query,
#                             self.plugin_runner.ressources)()
            CheckArguments(query, self.plugin_runner.ressources, None, None)()

        query2 = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "a", },
            ressource="wrong ressource",
            method="action1",
            request_method="GET"
        )
        with self.assertRaises(ArgumentError):
            CheckArguments(query2, self.plugin_runner.ressources, None, None)()

    def test_check_value_in(self):
        check_arguments = CheckArguments(self.query,
                                         self.plugin_runner.ressources,
                                         None,
                                         None)
        r = check_arguments.check_value_in("yes", ["yes", "no"])
        self.assertTrue(r)

        r = check_arguments.check_value_in("not", ["yes", "no"])
        self.assertFalse(r)

    def test_check_matches_re(self):
        check_arguments = CheckArguments(self.query,
                                         self.plugin_runner.ressources,
                                         None,
                                         None)
        regex = "^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+\.[a-zA-Z]{2,4}$"
        r = check_arguments.check_matches_re("noreply@noreply.com",
                                             regex)
        self.assertTrue(r)
        regex2 = "^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+\.[a-zA-Z]{2,4}$"
        r = check_arguments.check_matches_re("wrongmail",
                                             regex2)
        self.assertFalse(r)

    def test_check_not_exist(self):

        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressourceswrongcheck.yml",
            "tests.plugins", )

        with self.assertRaises(ArgumentCheckMethodNotFoundError):
            CheckArguments(self.query, plugin_runner.ressources, None, None)()

    """
    Check all
    """

    def test_check_all(self):
        try:
            self.plugin_runner(self.query)
        except:
            self.fail("error check all")

    def test_signature_not_required(self):
        query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GET"
        )
        error = None
        try:
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressources.yml",
                "tests.plugins",
                check_signature=False)
        except Exception as e:
            error = "error"
        self.assertTrue(not error)

    def test_signature_explicitely_required(self):
        query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            arguments={"login": "testzombie1", },
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            ressource="actions",
            method="action1",
            request_method="GET"
        )
        error = None
        try:
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressources.yml",
                "tests.plugins",
                check_signature=True)
        except Exception as e:
            error = "error"
        self.assertTrue(not error)

    def test_encode_base64(self):

        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressourceswithencodingrequired.yml",
            "tests.plugins")
        CheckArguments(self.query3, plugin_runner.ressources, None, None)()
        self.assertEqual(self.query3.arguments["login"], "testzombie1")

    def test_encode_base64_attribute_error(self):
        with self.assertRaises(DecodeAlgorithmNotFoundError):

            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressourceswithundecodableencoding.yml",
                "tests.plugins")
            CheckArguments(self.query3, plugin_runner.ressources, None, None)()

    def test_encode_base64_key_error(self):
        try:
            encodedzombie = base64.b64encode(b"testzombie1")
            query = Query(
                source="etab1",
                remote_ip="127.0.0.1",
                arguments={"login": encodedzombie, },
                signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                ressource="actions",
                method="action1",
                request_method="GET")
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data//noargressources.yml",
                "tests.plugins")
            CheckArguments(query, plugin_runner.ressources, None, None)()

        except Exception as e:
            self.assertTrue(isinstance(e, ExcaliburError))

    def test_all_error_raised(self):
        module = import_module('excalibur.exceptions')
        message = "message sublime"

        def str_caller(e):

            exception_class = getattr(module, e)
            exception_instance = exception_class(message)
            errorList = ['ExcaliburInternalError',
                         'ExcaliburClientError',
                         'ExcaliburError']
            if exception_instance.__class__.__name__ not in errorList:
                exceptionName = exception_instance.__class__.__name__
                self.assertEqual('%s : %s' % (exceptionName, message),
                                 exception_instance.__str__())
            else:
                self.assertEqual(message, exception_instance.__str__())

        [str_caller(error)
         for error in dir(module) if not error.startswith('_')]

    def test_key_errors(self):
        """
        KeyErrors should not be explicitly raised,
        they should instead be caught, and raise
        ExcaliburErrors.
        """

        """
        Generate queries with wrong values and launches checks
        """
        def query_generator(pos):
            query = Query(
                source="etab1",
                remote_ip="127.0.0.1",
                signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                arguments={"login": "testzombie1", },
                ressource="actions",
                method="action1",
                request_method="GET"
            )
            setattr(query, pos, "wrong")
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml", "./tests/data/sources.yml",
                "./tests/data/ressources.yml",
                "tests.plugins",
                query)

            # with self.assertRaises(ExcaliburError):
            try:
                CheckSource(query, plugin_runner.ressources, plugin_runner.sources(query.signature if
                                     query.signature else None,
                                     query.project,
                                     query.arguments if
                                     query.arguments else None), None)()
                CheckRequest(query, plugin_runner.ressources, None, None,)()
                CheckArguments(query, plugin_runner.ressources, None, None,)()
                CheckACL(query, None, None, plugin_runner.acl)()

            except Exception as e:
                self.assertTrue(isinstance(e, ExcaliburError))

            return query

        query_generator_by_arg = lambda pos: query_generator(pos)

        [query_generator_by_arg(attr) for attr in dir(self.query)
         if attr.startswith("_Query") and attr not in ["_Query__remote_ip"]]

    def test_check_not_implemented(self):
        c = Check()
        self.assertRaises(NotImplementedError, c.check)

    def test_multiple_api_keys(self):
        error = "no_error_yet"

        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sourceswithmultipleapikeys.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        try:
            plugin_runner(self.query)
        except Exception as e:
            error = "error"
        self.assertTrue(error == "no_error_yet")

    def test_multiple_api_keys_project_depth_and_etab_set_to_all(self):
        error = "no_error_yet"
        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml",
            "./tests/data/source_project_multiple_api_keys.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        query = Query(
            source=ALL_KEYWORD,
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GET",
            project="project1"
        )
        try:
            result = plugin_runner(query)
        except Exception as e:
            error = "error"
        self.assertTrue(error == "no_error_yet")

    def test_no_apikey_specified(self):
        error = "no_error_yet"

        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sourceswithnoapikey.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        try:
            plugin_runner(self.query)
        except Exception as e:
            error = "error"
        self.assertTrue(error == "no_error_yet")

    def test_no_ip_required(self):
        error = "no_error_yet"

        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sourceswithnoip.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        try:
            plugin_runner(self.query)
        except Exception as e:
            error = "error"
        self.assertTrue(error == "no_error_yet")

    def test_no_ip_specified(self):
        error = "no_error_yet"

        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sourceswithnoip.yml",
            "./tests/data/ressources.yml",
            "tests.plugins"
        )
        try:
            plugin_runner(self.query)
        except Exception as e:
            error = "error"
        self.assertTrue(error == "no_error_yet")

    def test_ressources_arguments_not_present(self):
        error = None
        try:
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressourceswithnoarguments.yml",
                "tests.plugins",
                check_signature=False)
            plugin_runner(self.query)
        except Exception as e:
            error = e
        self.assertTrue(not error)

    def test_ressources_arguments_empty_and_one_argument_provided(self):
        with self.assertRaises(ArgumentError):
            query = Query(
                source="etab1",
                remote_ip="127.0.0.1",
                signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                arguments={"login": "testzombie1", "uselessarg": "useless"},
                ressource="actions",
                method="action1",
                request_method="GET"
            )
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressourceswithemptyargs.yml",
                "tests.plugins",
                check_signature=False)
            plugin_runner(query)

    def test_optional_ressource_argument(self):
        error = None
        try:
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressourceswithoptionalargs.yml",
                "tests.plugins",
                check_signature=False)
            plugin_runner(self.query)
        except Exception as e:
            error = e
        self.assertTrue(not error)

    def test_optional_ressource_argument_and_matching_request_arg(self):
        error = None
        try:
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressourceswithoptionalargs.yml",
                "tests.plugins",
                check_signature=False)
            plugin_runner(self.query)
        except Exception as e:
            error = e
        self.assertTrue(not error)



    def test_encode_base64_runner(self):
        error = None
        try:
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressourceswithencodingrequired.yml",
                "tests.plugins",
                check_signature=True)
            plugin_runner(self.query3)
        except Exception as e:
            error = e
        self.assertTrue(not error)






    def test_optional_ressourcearg_matching_reqarg_and_exceeding_arg(self):
        with self.assertRaises(ArgumentError):
            query = Query(
                source="etab1",
                remote_ip="127.0.0.1",
                signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                arguments={
                    "login": "testzombie1", "uselessarg": "useless",
                    "exceedingarg": "exceeding"},
                ressource="actions",
                method="action1",
                request_method="GET"
            )
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressourceswithoptionalargs.yml",
                "tests.plugins",
                check_signature=False,
            )
            plugin_runner(query)

    def test_ressources_arguments_empty_and_no_argument_provided(self):
        error = "no_error_yet"
        query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="azertyuiop12345",
            arguments={},
            ressource="actions",
            method="action1",
            request_method="GET"
        )
        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressourceswithemptyargs.yml",
            "tests.plugins",
            check_signature=False)
        plugin_runner(query)
        self.assertTrue(error == "no_error_yet")

    def test_signature_not_in_generated_signatures(self):
        with self.assertRaises(WrongSignatureError):
            query = Query(
                source="etab1",
                remote_ip="127.0.0.1",
                signature="azertyuiop12345",
                arguments={"login": "testzombie1", },
                ressource="actions",
                method="action1",
                request_method="GET"
            )
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sourceswithmultipleapikeys.yml",
                "./tests/data/ressources.yml",
                "tests.plugins"
            )
            plugin_runner(query)


    def test_checks_with_optional_args_and_bad_argument_value(self):
        with self.assertRaises(ArgumentError):
            query = Query(
                source="etab1",
                remote_ip="127.0.0.1",
                signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                arguments={"login": "testzombie1", "uselessarg": "a"},
                ressource="actions",
                method="action2",
                request_method="GET"
            )
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressourceswithoptionalargs.yml",
                "tests.plugins",
                check_signature=False)
            plugin_runner(query)

    def test_checks_with_optional_args_and_no_arg(self):
        error = None
        try:
            query = Query(
                source="etab1",
                remote_ip="127.0.0.1",
                signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
                arguments={"login": "testzombie1"},
                ressource="actions",
                method="action2",
                request_method="GET"
            )
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressourceswithoptionalargs.yml",
                "tests.plugins",
                check_signature=False)
            plugin_runner(query)
        except Exception as e:
            error = e
        self.assertTrue(error is None)

    def test_missing_args(self):
        with self.assertRaises(ArgumentError):
            query = Query(
                source="etab1",
                remote_ip="127.0.0.1",
                signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",

                ressource="actions",
                method="action2",
                request_method="GET"
            )
            plugin_runner = PluginsRunner(
                "./tests/data/acl.yml",
                "./tests/data/sources.yml",
                "./tests/data/ressourceswithoptionalargs.yml",
                "tests.plugins",
                check_signature=False)
            plugin_runner(query)


if __name__ == '__main__':
    main()
