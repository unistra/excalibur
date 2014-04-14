#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from excalibur.decode import DecodeArguments
from excalibur.loader import ConfigurationLoader
from excalibur.check import CheckSource, CheckACL, CheckRequest, CheckArguments, Check
from excalibur.exceptions import SourceNotFoundError, IPNotAuthorizedError,\
    WrongSignatureError, NoACLMatchedError,RessourceNotFoundError,\
    MethodNotFoundError, HTTPMethodError, ArgumentError, \
    ArgumentCheckMethodNotFoundError,ExcaliburError,DecodeAlgorithmNotFoundError
from excalibur.core import PluginsRunner, Query
import base64
from importlib import import_module



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
        # Files
        self.plugin_runner = PluginsRunner(
            "./tests/data/acl.yml", "./tests/data/sources.yml", "./tests/data/ressources.yml", "tests.plugins", self.query)

    """
    Check Source
    """

    def test_check_source(self):
        """ test check sources """
        try:
            check_source = CheckSource(self.query,self.plugin_runner.sources)
            check_source.check()
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
            check_source = CheckSource(query1,self.plugin_runner.sources)
            check_source.check()

    def test_check_source_ip_not_authorized(self):
        """ test check sources """
        query2 = Query(
            source="etab1",
            remote_ip="9.9.9.9",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GET"
        )
        with self.assertRaises(IPNotAuthorizedError):
            check_source = CheckSource(query2,self.plugin_runner.sources)
            check_source.check()

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
            check_source = CheckSource(query3,self.plugin_runner.sources)
            check_source.check()

    """
    Check ACL
    """

    def test_check_acl(self):
        """ test check acl """
        try:
            check_acl = CheckACL(self.plugin_runner.acl)
            check_acl.check(self.plugin_runner.query.source,
                            self.plugin_runner.query.ressource, self.plugin_runner.query.method)
        except:
            self.fail("Error check acl")

    def test_check_acl_no_matched(self):
        """ test check acl """
        method = "actionull"
        with self.assertRaises(NoACLMatchedError):
            check_acl = CheckACL(self.plugin_runner.acl)
            check_acl.check(
                self.plugin_runner.query.source, self.plugin_runner.query.ressource, method)

        with self.assertRaises(NoACLMatchedError):
            check_acl = CheckACL(self.plugin_runner.acl)
            check_acl.check(
                self.plugin_runner.query.source, self.plugin_runner.query.ressource, 
                self.plugin_runner.query.method, project="keyerror")

        plugin_runner = PluginsRunner(
            "./tests/data/acl_projects.yml", "./tests/data/sources.yml", "./tests/data/ressources.yml", "tests.plugins", self.query)

        with self.assertRaises(NoACLMatchedError):
            check_acl = CheckACL(plugin_runner.acl)
            check_acl.check(
                self.plugin_runner.query.source, self.plugin_runner.query.ressource, 
                "wrongmethod", project="project1")

    """
    Check Request
    """

    def test_check_request(self):
        """ test check request """
        try:
            check_request = CheckRequest(self.plugin_runner.ressources)
            check_request.check(self.plugin_runner.query.request_method, self.plugin_runner.query.ressource,
                                self.plugin_runner.query.method, self.plugin_runner.query.arguments)
        except:
            self.fail("error check request")

    def test_check_request_ressource_not_found(self):
        """ test check request """
        ressource = "ressourcenull"
        with self.assertRaises(RessourceNotFoundError):
            check_request = CheckRequest(self.plugin_runner.ressources)
            check_request.check(self.plugin_runner.query.request_method, ressource,
                                self.plugin_runner.query.method, self.plugin_runner.query.arguments)

    def test_check_request_method_not_found(self):
        """ test check request """
        method = "methodnull"
        with self.assertRaises(MethodNotFoundError):
            check_request = CheckRequest(self.plugin_runner.ressources)
            check_request.check(self.plugin_runner.query.request_method,
                                self.plugin_runner.query.ressource, method, self.plugin_runner.query.arguments)

    def test_check_request_method_http_error(self):
        """ test check request """
        request_method = "GETnull"
        with self.assertRaises(HTTPMethodError):
            check_request = CheckRequest(self.plugin_runner.ressources)
            check_request.check(request_method, self.plugin_runner.query.ressource,
                                self.plugin_runner.query.method, self.plugin_runner.query.arguments)

    def test_check_request_args_error(self):
        """ test check request """
        arguments = "argumentsnull"
        with self.assertRaises(ArgumentError):
            check_request = CheckRequest(self.plugin_runner.ressources)
            check_request.check(self.plugin_runner.query.request_method,
                                self.plugin_runner.query.ressource, self.plugin_runner.query.method, arguments)

        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml", "./tests/data/sources.yml", "./tests/data/ressourceswrongcheck.yml", "tests.plugins", self.query)

        with self.assertRaises(ArgumentError):
            check_request = CheckRequest(plugin_runner.ressources)
            check_request.check(self.plugin_runner.query.request_method,
                                self.plugin_runner.query.ressource, "action2", arguments)



    """
    Check arguments
    """

    def test_check_arguments(self):
        """ test check arguments """
        try:
            decode_arguments = DecodeArguments(self.plugin_runner.ressources)
            decode_arguments.decode(
                self.plugin_runner.query.ressource, self.plugin_runner.query.method, self.plugin_runner.query.arguments)

            check_arguments = CheckArguments(self.plugin_runner.ressources)
            check_arguments.check(self.plugin_runner.query.arguments,
                                  self.plugin_runner.query.ressource, self.plugin_runner.query.method)
        except:
            self.fail("error check arguments")

    def test_check_arguments_error(self):
        """ test check arguments """
        arguments = {"login": "a", }
        with self.assertRaises(ArgumentError):
            decode_arguments = DecodeArguments(self.plugin_runner.ressources)
            decode_arguments.decode(
                self.plugin_runner.query.ressource, self.plugin_runner.query.method, arguments)

            check_arguments = CheckArguments(self.plugin_runner.ressources)
            check_arguments.check(
                arguments, self.plugin_runner.query.ressource, self.plugin_runner.query.method)

        with self.assertRaises(ArgumentError):
            check_arguments.check(
                arguments, "wrong ressource", self.plugin_runner.query.method)

    def test_check_value_in(self):
        check_arguments = CheckArguments(self.plugin_runner.ressources)
        r = check_arguments.check_value_in("yes", ["yes", "no"])
        self.assertTrue(r)

        r = check_arguments.check_value_in("not", ["yes", "no"])
        self.assertFalse(r)


    def test_check_matches_re(self):
        check_arguments = CheckArguments(self.plugin_runner.ressources)
        r = check_arguments.check_matches_re("noreply@noreply.com", 
            "^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+\.[a-zA-Z]{2,4}$")
        self.assertTrue(r)
        r = check_arguments.check_matches_re("wrongmail", 
            "^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+\.[a-zA-Z]{2,4}$")
        self.assertFalse(r)


    def test_check_not_exist(self):
        plugin_runner = PluginsRunner(
            "./tests/data/acl.yml", "./tests/data/sources.yml", "./tests/data/ressourceswrongcheck.yml", "tests.plugins", self.query)
        check_arguments = CheckArguments(plugin_runner.ressources)
        with self.assertRaises(ArgumentCheckMethodNotFoundError):
            check_arguments.check(
                plugin_runner.query.arguments, plugin_runner.query.ressource, plugin_runner.query.method)


    """
    Check all
    """

    def test_check_all(self):
        try:
            self.plugin_runner.check_all()
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
                query,
                check_signature=False)
         except Exception as e:
             error = "error"
         self.assertTrue(error == None)
         
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
                query,
                check_signature=True)
         except Exception as e:
             error = "error"
         self.assertTrue(error == None)
         
    def test_encode_base64(self):
       
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
        "./tests/data/ressourceswithencodingrequired.yml",
        "tests.plugins",
        query)
        decode_arguments = DecodeArguments(plugin_runner.ressources)
        decode_arguments.decode(
            plugin_runner.query.ressource, plugin_runner.query.method,
            plugin_runner.query.arguments)
        self.assertEqual(query.arguments["login"],"testzombie1")
        
    def test_encode_base64_attribute_error(self):
        with self.assertRaises(DecodeAlgorithmNotFoundError):
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
            "./tests/data/ressourceswithundecodableencoding.yml",
            "tests.plugins",
            query)
            decode_arguments = DecodeArguments(plugin_runner.ressources)
            decode_arguments.decode(
                plugin_runner.query.ressource, plugin_runner.query.method,
                plugin_runner.query.arguments)
        
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
            "tests.plugins",
            query)
            decode_arguments = DecodeArguments(plugin_runner.ressources)
            decode_arguments.decode(
                plugin_runner.query.ressource, plugin_runner.query.method,
                plugin_runner.query.arguments)
            
        except Exception as e: 
             self.assertTrue(isinstance(e,ExcaliburError))
           
    def test_all_error_risen(self): 
        module = import_module('excalibur.exceptions') 
        message = "message sublime"
        def str_caller(e):
            exception_class= getattr(module,e)
             
            exception_instance = exception_class(message)
            if not exception_instance.__class__.__name__ in ['ExcaliburInternalError','ExcaliburClientError','ExcaliburError']:
                self.assertEqual ('%s : %s' % (exception_instance.__class__.__name__, message),exception_instance.__str__())
            else:
                self.assertEqual (message,exception_instance.__str__())
             
             
        [str_caller(error) for error in dir(module) if not error.startswith('_') ]
        
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
            setattr(query,pos,"wrong")
            plugin_runner = PluginsRunner(
            "./tests/data/acl.yml", "./tests/data/sources.yml", 
            "./tests/data/ressources.yml", 
            "tests.plugins", 
            query)
            
            #with self.assertRaises(ExcaliburError):
            try:
                CheckSource(query,plugin_runner.sources).check()
                CheckRequest(plugin_runner.ressources).check(
                    plugin_runner.query.request_method,
                    plugin_runner.query.ressource, 
                    plugin_runner.query.method, 
                    plugin_runner.query.arguments)
                CheckArguments(plugin_runner.ressources).check(
                    plugin_runner.query.arguments,
                    plugin_runner.query.ressource,
                    plugin_runner.query.method)
                CheckACL(plugin_runner.acl).check(
                    plugin_runner.query.source,
                    plugin_runner.query.ressource,
                    plugin_runner.query.method,
                    project=None)
                
            except Exception as e:
                self.assertTrue(isinstance(e,ExcaliburError))
            
            return query
            
        query_generator_by_arg = lambda pos : query_generator(pos)
        
        [query_generator_by_arg(attr) for attr in dir(self.query) \
         if attr.startswith("_Query") and not attr in ["_Query__remote_ip"]]
        

    def test_check_notimplemented(self):
        c = Check()
        self.assertRaises(NotImplementedError, c.check)

if __name__ == '__main__':
    main()
