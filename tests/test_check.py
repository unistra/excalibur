#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from excalibur.decode import DecodeArguments
from excalibur.loader import ConfigurationLoader
from excalibur.check import CheckSource, CheckACL, CheckRequest, CheckArguments
from excalibur.exceptions import SourceNotFoundError, IPNotAuthorizedError, WrongSignatureError, NoACLMatchedError,\
    RessourceNotFoundError, MethodNotFoundError, HTTPMethodError, ArgumentError, ArgumentCheckMethodNotFoundError
from excalibur.core import PluginsRunner, Query


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
            check_source = CheckSource(self.plugin_runner.sources)
            check_source.check(self.plugin_runner.query.source, self.plugin_runner.query.remote_ip,
                               self.plugin_runner.query.signature, self.plugin_runner.query.arguments)
        except:
            self.fail("Error check source")

    def test_check_source_not_found(self):
        """ test check sources """
        source = "etabnull"
        with self.assertRaises(SourceNotFoundError):
            check_source = CheckSource(self.plugin_runner.sources)
            check_source.check(source, self.plugin_runner.query.remote_ip,
                               self.plugin_runner.query.signature, self.plugin_runner.query.arguments)

    def test_check_source_ip_not_authorized(self):
        """ test check sources """
        remote_ip = "9.9.9.9"
        with self.assertRaises(IPNotAuthorizedError):
            check_source = CheckSource(self.plugin_runner.sources)
            check_source.check(self.plugin_runner.query.source, remote_ip,
                               self.plugin_runner.query.signature, self.plugin_runner.query.arguments)

    def test_check_source_signature_error(self):
        """ test check sources """
        signature = "ERROR"
        with self.assertRaises(WrongSignatureError):
            check_source = CheckSource(self.plugin_runner.sources)
            check_source.check(self.plugin_runner.query.source, self.plugin_runner.query.remote_ip,
                               signature, self.plugin_runner.query.arguments)

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

    """
    Check all
    """

    def test_check_all(self):
        try:
            self.plugin_runner.check_all()
        except:
            self.fail("error check all")


if __name__ == '__main__':
    main()
