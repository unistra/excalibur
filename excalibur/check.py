# -*- coding: utf-8 -*-
import re

from excalibur.exceptions import ArgumentError,\
    ArgumentCheckMethodNotFoundError, CheckMethodError,\
    NoACLMatchedError, RessourceNotFoundError, MethodNotFoundError,\
    HTTPMethodError, SourceNotFoundError, \
    IPNotAuthorizedError, WrongSignatureError
from excalibur.decode import DecodeArguments
from excalibur.utils import add_args_then_encode,\
    ALL_KEYWORD, SOURCE_SEPARATOR, sources_list_or_list,\
    all_sources_or_sources_list_or_list,\
    is_simple_request_and_source_not_found, ip_found_in_sources,\
    get_api_keys_by_sources

import itertools


class Check(object):

    """
    Check parent class.
    Mostly empty.
    """

    def check(self):
        raise NotImplementedError


class CheckArguments(Check):

    """
    Class ensuring argument consistency.
    Search the ressources.yml's argument entry
    to find all registered constraints and launch
    matching methods based on naming convention.
    By now, checks are two arguments methods that
    compare a received value to an expected value.
    The comparator is not dynamically obtained, it
    is in the body of the method.
    """

    @DecodeArguments
    def __init__(self, query, ressources, sources, acl,
                 sha1check=True, ipcheck=True):

        self.ressources = ressources
        self.arguments = query.arguments
        self.ressource = query.ressource
        self.method = query.method
        self.query = query

    def __call__(self):

        # Keep trace of arguments that do not pass tests.
        errors = {}
        targeted_ressource = self.ressources[self.ressource]\
            if self.ressource in self.ressources.keys() else None

        if targeted_ressource is None:
            raise ArgumentError("unexpected argument")

        if "arguments" in targeted_ressource[self.method].keys():

            args = targeted_ressource[self.method][
                "arguments"]
            for argument_name in self.arguments:
                try:
                    check_list = args[argument_name]["checks"]\
                        if args is not None else []
                except KeyError as k:
                    raise ArgumentError("unexpected argument %s"
                                        % argument_name)
                for check in check_list:
                    try:
                        check_method_name = self.format(check)
                        check_method = getattr(self, check_method_name)
                        check_parameter = args[argument_name]["checks"][check]
                        value_to_check = self.arguments[argument_name]
                        if not check_method(value_to_check, check_parameter):
                            errors[argument_name] = check
                    except AttributeError as a:
                        raise ArgumentCheckMethodNotFoundError(
                            check_method_name)
                    except Exception as e:
                        raise CheckMethodError(e)

        if errors:
            raise ArgumentError("The check list did not pass", errors)

    def check_min_length(self, argument_value, length):
        return len(argument_value) >= length

    def check_max_length(self, argument_value, length):
        return len(argument_value) <= length

    def check_value_in(self, argument_value, choices):
        return argument_value in choices

    def check_matches_re(self, argument_value, re_string):
        regex = re.compile(re_string)

        return regex.match(argument_value) is not None

    @staticmethod
    def format(x):
        return "check_" + x.replace(" ", "_")


class CheckACL(Check):

    """
    Checks method and ressources allowances. ACLs are defined
    in the acl.yml file.
    Right now, if we want to be enable requests that parse all sources,
    acl verification MUST be disabled when the source does not match any entry
    in the acl file.
    Yet, checking methods availability is a good principle.
    An equivalent of this check could happen when the method in the core
    is about to be called.
    """

    def __init__(self, query, ressources, sources, acl,
                 sha1check=True, ipcheck=True):
        self.sources = sources
        self.acl = acl
        self.source = query.source
        self.ressource = query.ressource
        self.method = query.method
        self.project = query.project

    def __call__(self):
        targets = all_sources_or_sources_list_or_list(
            self.source, self.sources)

        allowed_method_suffixes = []
        project = self.project or (
            'default' if hasattr(self.acl, 'default') else self.project)
        try:
            for target in targets:
                allowed_method_suffixes +=\
                    self.acl[project][target][self.ressource]\
                    if project else self.acl[target][self.ressource]
            if self.method not in allowed_method_suffixes:
                raise NoACLMatchedError(
                    "%s/%s" % (self.ressource, self.method))
        except KeyError as k:
            raise NoACLMatchedError(
                "%s/%s" % (self.ressource, self.method))


class CheckRequest(Check):

    """
    Check request legitimacy based on various
    criteria registered in the ressources.yml file.
    """

    def __init__(self, query, ressources, sources, acl,
                 sha1check=True, ipcheck=True):

        self.ressources = ressources
        self.http_method = query.request_method
        self.method = query.method
        self.arguments = query.arguments
        self.ressource = query.ressource

    def __call__(self):
        try:
            # sure??
            if self.ressource not in self.ressources.keys():
                raise RessourceNotFoundError(self.ressource)

            if self.method not in self.ressources[self.ressource]:
                raise MethodNotFoundError(self.method)

            targeted_method = self.ressources[self.ressource][self.method]
            if "request method" in\
                targeted_method.keys()\
                and self.http_method !=\
                    targeted_method["request method"]:
                raise HTTPMethodError(
                    targeted_method["request method"])

            if "arguments" in targeted_method.keys():
                # method requires strictly no arguments and received arguments
                # contained parameters
                if not targeted_method['arguments']\
                        and self.arguments != {}:
                    raise ArgumentError("%s only supports no arguments "
                                        "requests, received : %s" % (
                                            self.method, self.arguments))

                # wrong format in arguments received from the request
                if not isinstance(self.arguments, dict):
                    raise ArgumentError("%s is not a supported format" % (
                        targeted_method))

                # required args are missing
                if not self.all_required_args_found(
                        targeted_method["arguments"]):
                    raise ArgumentError("received arguments do no match :"
                                        " %s required arguments : %s)" % (
                                            self.arguments,
                                            targeted_method["arguments"]))

                # args found neither in required nor optional args found
                if not set(self.arguments.keys()).issubset(
                        set(targeted_method['arguments'].keys()if
                            targeted_method['arguments']is not None else[])):
                    raise ArgumentError("exceeding parameters")

        except KeyError as k:
            raise ArgumentError("key not found in sources")

    def all_required_args_found(self, required):
        received = self.required_received_params(required).keys()
        expected = self.required_params(required).keys()
        return set(received) == set(expected)

    def required_params(self, args):

        return {k: v for k, v in args.items() if "optional" not in v.keys()
                or v['optional']is not True}\
            if args is not None else{}

    def required_received_params(self, args):
        return {k: v for k, v in self.arguments.items() if k in
                self.required_params(args).keys()}


class CheckSource(Check):
    """
    Check source ensures that the right api_key is found
    in the plugin's configuration which is targeted by the request.
    It is also the application spot where the ip can be checked.
    """

    def __init__(self, query, ressources, sources, acl,
                 sha1check=True, ipcheck=True):

        self.sources = sources
        self.source = query.source
        self.ip = query.remote_ip
        self.signature = query.signature
        self.arguments = query.arguments
        self.sha1check = sha1check
        self.ipcheck = ipcheck

        self.disable_check("apikey", "sha1check")
        self.disable_check("ip", "ipcheck")

    def disable_check(self, key_name, property_name):
        # for yaml loaded classes to work, disable check should be modified
        if getattr(self, property_name) and \
           self.source in self.sources.keys() and \
           key_name not in self.sources[self.source]:
            setattr(self, property_name, False)

    def __call__(self):
        """

        """

        try:
            if is_simple_request_and_source_not_found(self.source,
                                                      self.sources):
                raise SourceNotFoundError("Unknown source %s" % self.source)
            if self.ipcheck:
                # Check if IP is authorized
                ip_authorized = ip_found_in_sources(self.source, self.sources, self.ip)
                if not ip_authorized:
                    raise IPNotAuthorizedError(self.ip)
            # Signature check
            if self.source != ALL_KEYWORD and self.sha1check:
                # The request has to be allowed for all the sources it targets
                targets = sources_list_or_list(self.source)
                api_keys_by_sources = get_api_keys_by_sources(self.sources,
                                                              targets)
                arguments_list = sorted(self.arguments)

                # If multiple api_keys are registered
                for target_name, api_keys in api_keys_by_sources.items():
                    if len(api_keys) > 1:
                        signkeys = [add_args_then_encode(signature,
                                                         arguments_list,
                                                         self.arguments)
                                    for signature in api_keys]
                        if self.signature not in signkeys:
                            raise WrongSignatureError(self.signature)
                    # If there is only one api_key
                    else:
                        signkey = add_args_then_encode(api_keys[0],
                                                       arguments_list,
                                                       self.arguments)
                        if self.signature != signkey:
                            raise WrongSignatureError(self.signature)
        except KeyError as k:
            raise SourceNotFoundError("key was not found in sources")
        except TypeError as t:
            raise SourceNotFoundError("key was not found in sources")
