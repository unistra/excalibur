#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from excalibur.decode import DecodeArguments
from excalibur.loader import ConfigurationLoader
from excalibur.check import CheckSource, CheckACL, CheckRequest, CheckArguments
from excalibur.exceptions import SourceNotFoundError, IPNotAuthorizedError, WrongSignatureError, NoACLMatchedError,\
RessourceNotFoundError, MethodNotFoundError, HTTPMethodError, ArgumentError, ArgumentCheckMethodNotFoundError
from excalibur.utils import check_all


class CheckTest(TestCase):
    """
    Unit test for check method
    Warning : "Params" of the setUp method need to be valid with
    your yaml files
    """

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

    """
    Check Source
    """

    def test_check_source(self):
        """ test check sources """
        try:
            check_source = CheckSource(self.sources)
            check_source.check(self.source, self.remote_ip, 
                           self.signature, self.arguments)
        except:
            self.fail("Error check source")

    def test_check_source_not_found(self):
        """ test check sources """
        source = "etabnull"
        with self.assertRaises(SourceNotFoundError):
            check_source = CheckSource(self.sources)
            check_source.check(source, self.remote_ip, 
                           self.signature, self.arguments)

    def test_check_source_ip_not_authorized(self):
        """ test check sources """
        remote_ip = "9.9.9.9"
        with self.assertRaises(IPNotAuthorizedError):
            check_source = CheckSource(self.sources)
            check_source.check(self.source, remote_ip, 
                           self.signature, self.arguments)

    def test_check_source_signature_error(self):
        """ test check sources """
        signature = "ERROR"
        with self.assertRaises(WrongSignatureError):
            check_source = CheckSource(self.sources)
            check_source.check(self.source, self.remote_ip, 
                           signature, self.arguments)
    
    """
    Check ACL
    """

    def test_check_acl(self):
        """ test check acl """
        try:
            check_acl = CheckACL(self.acl)
            check_acl.check(self.source, self.ressource, self.method)
        except:
            self.fail("Error check acl")

    def test_check_acl_no_matched(self):
        """ test check acl """
        method = "actionull"
        with self.assertRaises(NoACLMatchedError):
            check_acl = CheckACL(self.acl)
            check_acl.check(self.source, self.ressource, method)

    """
    Check Request
    """         

    def test_check_request(self):
        """ test check request """
        try:
            check_request = CheckRequest(self.ressources)
            check_request.check(self.request_method, self.ressource, self.method, self.arguments)
        except:
            self.fail("error check request")

    def test_check_request_ressource_not_found(self):
        """ test check request """
        ressource = "ressourcenull"
        with self.assertRaises(RessourceNotFoundError):
            check_request = CheckRequest(self.ressources)
            check_request.check(self.request_method, ressource, self.method, self.arguments)

    def test_check_request_method_not_found(self):
        """ test check request """
        method = "methodnull"
        with self.assertRaises(MethodNotFoundError):
            check_request = CheckRequest(self.ressources)
            check_request.check(self.request_method, self.ressource, method, self.arguments)

    def test_check_request_method_http_error(self):
        """ test check request """
        request_method = "GETnull"
        with self.assertRaises(HTTPMethodError):
            check_request = CheckRequest(self.ressources)
            check_request.check(request_method, self.ressource, self.method, self.arguments)

    def test_check_request_args_error(self):
        """ test check request """
        arguments = "argumentsnull"
        with self.assertRaises(ArgumentError):
            check_request = CheckRequest(self.ressources)
            check_request.check(self.request_method, self.ressource, self.method, arguments)

    """
    Check arguments
    """    

    def test_check_arguments(self):
        """ test check arguments """
        try:
            decode_arguments = DecodeArguments(self.ressources)
            decode_arguments.decode(self.ressource, self.method, self.arguments)

            check_arguments = CheckArguments(self.ressources)
            check_arguments.check(self.arguments, self.ressource, self.method)
        except:
            self.fail("error check arguments")

    def test_check_arguments_error(self):
        """ test check arguments """
        arguments = { "login": "a", }
        with self.assertRaises(ArgumentError):
            decode_arguments = DecodeArguments(self.ressources)
            decode_arguments.decode(self.ressource, self.method, arguments)

            check_arguments = CheckArguments(self.ressources)
            check_arguments.check(arguments, self.ressource, self.method)

    """
    Check all
    """
    def test_check_all(self):
        try:
            check_all(self.acl, self.sources, self.ressources, self.request_method, 
                self.source, self.ressource, self.method, self.remote_ip, self.arguments, self.signature)
        except:
            self.fail("error check all")




if __name__ == '__main__':
    main()