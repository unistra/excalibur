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
    DecodeAlgorithmNotFoundError, SourcesNotParsable
from excalibur.core import PluginsRunner, Query
import base64
from importlib import import_module
from excalibur.utils import ALL_KEYWORD, generate_RSA

class HTTPSigTest(TestCase):
    """
    test httpsig
    """

    def setUp(self):
        my_tuple = generate_RSA(bits=1024)
        for truc in my_tuple:
            print(truc)

        self.query = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GET",
            project="project1"
        )
 
        self.query2 = Query(
            source="etab1",
            remote_ip="9.9.9.9",
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            arguments={"login": "testzombie1", },
            ressource="actions",
            method="action1",
            request_method="GET",
            project="project1"
        )
        encodedzombie = base64.b64encode(b"testzombie1")
        self.query3 = Query(
            source="etab1",
            remote_ip="127.0.0.1",
            arguments={"login": encodedzombie, },
            signature="c08b3ff9dff7c5f08a1abdfabfbd24279e82dd10",
            ressource="actions",
            method="action1",
            request_method="GET",
            project="project1"
        )
        # Files
        self.plugin_runner = PluginsRunner(
            "./tests/data/acl.yml",
            "./tests/data/sources.yml",
            "./tests/data/ressources.yml",
            "tests.plugins",
            "./tests/data/sign_keys")
 
    """
    Check Source
    """
 
    def test_check_source(self):
        """ test check sources """
        try:
            CheckSource(
                self.query, None,
                self.plugin_runner.sources(project=self.query.project), None)()
 
        except:
            self.fail("Error check source")
    