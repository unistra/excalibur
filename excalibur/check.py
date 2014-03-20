# -*- coding: utf-8 -*-
import hashlib
import re

from excalibur.exceptions import ArgumentError, ArgumentCheckMethodNotFoundError, CheckMethodError,\
    NoACLMatchedError, RessourceNotFoundError, MethodNotFoundError, HTTPMethodError, SourceNotFoundError, \
    IPNotAuthorizedError, WrongSignatureError


class Check(object):

    """
    Classe mere pour implementer les Checks.
    """

    def check(self):
        raise NotImplementedError


class CheckArguments(Check):

    """
    Classe verifiant la consistance des arguments.

    Pour implementer un nouveau test, il suffit d'implementer une nouvelle methode qui
    doit se nommer check_nomdutest. Les arguments passes doivent etre la valeur a tester
    et une valeur servant au test. La valeur de retour doit etre un booleen.
    """

    def __init__(self, ressources):
        self.ressources = ressources

    def check(self, arguments, ressource, method):
        errors = {}  # Garde la trace des arguments qui ont echoue aux checks
        for argument_name in arguments:
            # Construction et verification de la batterie de checks
            # (check_list)
            try:
                check_list = self.ressources[ressource][method][
                    "arguments"][argument_name]["checks"]
            except KeyError:
                raise ArgumentError("unexpected argument %s" % argument_name)

            for check in check_list:
                try:
                    check_method_name = "check_" + check.replace(" ", "_")
                    check_method = getattr(self, check_method_name)
                    check_parameter = self.ressources[ressource][method][
                        "arguments"][argument_name]["checks"][check]
                    value_to_check = arguments[argument_name]

                    if not check_method(value_to_check, check_parameter):
                        errors[argument_name] = check
                except AttributeError:
                    raise ArgumentCheckMethodNotFoundError(check_method_name)
                except Exception as e:
                    # Erreur dans la 'check method'
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


class CheckACL(Check):

    """
    Verifie les acces aux ressources et methodes. Les ACL sont definies dans
    le fichier acl.yml.
    """

    def __init__(self, acl):
        self.acl = acl

    def check(self, source, ressource, method, project=None):
        if project:
            if method not in self.acl[project][source][ressource]:
                raise NoACLMatchedError("%s/%s" % (ressource, method))
        else:
            if method not in self.acl[source][ressource]:
                raise NoACLMatchedError("%s/%s" % (ressource, method))


class CheckRequest(Check):

    """
    Verifie la requete realisee sur divers criteres. La verification d'un critere
    est effectuee par l'appel de l'une des methodes definies ci-dessous.

    Les criteres attendus sont definis dans le fichier ressources.yml.
    """

    def __init__(self, ressources):
        self.ressources = ressources

    def check(self, http_method, ressource, method, arguments):
        if ressource not in self.ressources:
            raise RessourceNotFoundError(ressource)
        if method not in self.ressources[ressource]:
            raise MethodNotFoundError(method)
        if http_method != self.ressources[ressource][method]["request method"]:
            raise HTTPMethodError(
                self.ressources[ressource][method]["request method"])

        expected_nb_arguments = len(
            self.ressources[ressource][method]["arguments"])
        received_nb_arguments = len(arguments)

        if expected_nb_arguments != received_nb_arguments:
            raise ArgumentError("Unexpected number of arguments: %i (expected %i)" % (
                received_nb_arguments, expected_nb_arguments))


class CheckSource(Check):

    """
    S'assure que la source est legitime en suivant les donnees presentes
    dans le fichier sources.yml.
    """

    def __init__(self, sources):
        self.sources = sources

    def check(self, source, ip, signature, arguments):
        if source not in self.sources:
            raise SourceNotFoundError("Unknown source %s" % source)

        # Check if IP is authorized
        if ip not in self.sources[source]["ip"]:
            raise IPNotAuthorizedError(ip)

        # Signature check
        arguments_list = sorted(arguments)

        to_hash = self.sources[source]["apikey"]

        for argument in arguments_list:
            to_hash += (argument + arguments[argument])

        signkey = hashlib.sha1(to_hash.encode("utf-8")).hexdigest()

        if signature != signkey:
            raise WrongSignatureError(signature)
