# -*- coding: utf-8 -*-
import re

from excalibur.exceptions import ArgumentError,\
    ArgumentCheckMethodNotFoundError, CheckMethodError,\
    NoACLMatchedError, RessourceNotFoundError, MethodNotFoundError,\
    HTTPMethodError, SourceNotFoundError, \
    IPNotAuthorizedError, WrongSignatureError
from excalibur.decode import DecodeArguments
from excalibur.utils import add_args_then_encode
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
        if self.source != "all":
            try:
                allowed_method_suffixes = self.acl[self.project]\
                    [self.source]\
                    [self.ressource] if self.project else self.acl[self.source]\
                    [self.ressource]
                if self.method not in allowed_method_suffixes:
                    raise NoACLMatchedError(
                        "%s/%s" % (self.ressource, self.method))
            except KeyError:
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
            if self.ressource not in self.ressources:
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
#         self.disable_check("ip", "ipcheck")

    def disable_check(self, key_name, property_name):
        if getattr(self, property_name) and isinstance(self.sources, dict) and \
           self.source in self.sources and \
           key_name not in self.sources[self.source]:
            setattr(self, property_name, False)

    def __call__(self):
        """

        """

        try:
            if self.source != "all" and self.source not in \
                    self.sources:
                raise SourceNotFoundError("Unknown source %s" % self.source)
            ip_authorized = True
#             if self.source != "all" and self.ipcheck:
#             if self.ipcheck:
                # Check if IP is authorized
            ip_authorized = True
            for ip_list in [it["ip"] for it in self.sources.values() if "ip" in list(it.keys())]:
                if not [ip for ip in ip_list if re.match(ip, self.ip)]:
                    ip_authorized = False

            if not ip_authorized:
                raise IPNotAuthorizedError(self.ip)
            # Signature check
            if self.source != "all" and self.sha1check:
                source_api_key = self.sources[self.source]["apikey"]
                arguments_list = sorted(self.arguments)

                # if multiple api_keys are registered
                if isinstance(source_api_key, list):
                    signkeys = [add_args_then_encode(signature,
                                                     arguments_list,
                                                     self.arguments)
                                for signature in source_api_key]
                    if self.signature not in signkeys:
                        raise WrongSignatureError(self.signature)
                # if there is only one api_key
                else:
                    signkey = add_args_then_encode(source_api_key,
                                                   arguments_list,
                                                   self.arguments)
                    if self.signature != signkey:
                        raise WrongSignatureError(self.signature)

        except KeyError as k:
            raise SourceNotFoundError("key was not found in sources")
        except TypeError as t:
            raise SourceNotFoundError("key was not found in sources")
