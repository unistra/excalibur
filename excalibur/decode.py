# -*- coding: utf-8 -*-
"""
Module qui permet de gerer l'encodage de certains arguments. Comme par exemple,
l'encodage en base64 pour palier au probleme de
caracteres speciaux non geres par
les urls.
"""
from excalibur.exceptions import ArgumentError, DecodeAlgorithmNotFoundError
import base64


class DecodeArguments(object):

    """
    Classe contenant les differents algorithmes de decodage.

    Pour implementer un nouvel algorithme, une methode suivant la
    regle de nommage suivante decode_nomalgo doit recevoir la
    valeur en argument. Et retourner la valeur decodee.
    """

    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        self.cls = owner
        self.obj = instance
        return self.__call__

    def __call__(self, *k, **kw):
        """
        Pour chacun des arguments passes, regarde s'il doit etre decode.
        Et si c'est le cas, appelle la methode correspondante.
        """
        self.ressources = k[1]
        self.ressource = k[0].ressource
        self.method_name = k[0].method
        self.arguments = k[0].arguments

        if self.ressource not in self.ressources.keys():
            raise ArgumentError("ressource not found")

        ressource = self.ressources[self.ressource]

        # the check is optionnal, it occurs only if there is an entry
        # "arguments
        try:
            if "arguments" in ressource[self.method_name].keys():
                arguments = ressource[self.method_name]["arguments"]
                if arguments:
                    for argument_name in self.arguments:
                        if "encoding" in arguments[argument_name]:
                            algo = arguments[argument_name]["encoding"]
                            method = getattr(self, "decode_" + algo)
                            self.arguments[argument_name] = method(
                                self.arguments[argument_name])
        except KeyError:
            raise ArgumentError('Wrong ressource configuration: key not found for method %s' % self.method_name)
        except AttributeError:
            raise DecodeAlgorithmNotFoundError(algo)

        return self.f(self.obj, *k, **kw)

    def decode_base64(self, value):
        """
        Implemente le decodage base64.
        """

        # base64 decoding returns bytestrings
        decoded_value = base64.b64decode(value).decode("utf-8")
        return decoded_value

    def decode_base64url(self, value):
        """
        safeb64
        """
        decoded_value = base64.urlsafe_b64decode(value.encode('utf-8'))\
            .decode("utf-8")
        return decoded_value
