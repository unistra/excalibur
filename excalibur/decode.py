# -*- coding: utf-8 -*-
"""
Module qui permet de gerer l'encodage de certains arguments. Comme par exemple,
l'encodage en base64 pour palier au probleme de caracteres speciaux non geres par
les urls.
"""
from excalibur.exceptions import ArgumentError, DecodeAlgorithmNotFoundError


class DecodeArguments(object):

    """
    Classe contenant les differents algorithmes de decodage.

    Pour implementer un nouvel algorithme, une methode suivant la
    regle de nommage suivante decode_nomalgo doit recevoir la
    valeur en argument. Et retourner la valeur decodee.
    """

    def __init__(self, ressources):
        self.ressources = ressources

    def decode(self, ressource, method_name, arguments):
        """
        Pour chacun des arguments passes, regarde s'il doit etre decode.
        Et si c'est le cas, appelle la methode correspondante.
        """
        try:
            for argument_name in arguments:
                if "encoding" in self.ressources[ressource][method_name]["arguments"][argument_name]:
                    algo = self.ressources[ressource][method_name][
                        "arguments"][argument_name]["encoding"]
                    method = getattr(self, "decode_" + algo)
                    arguments[argument_name] = method(arguments[argument_name])
        except KeyError:
            raise ArgumentError(argument_name)
        except AttributeError:
            raise DecodeAlgorithmNotFoundError(algo)

    def decode_base64(self, value):
        """
        Implemente le decodage base64.
        """

        # base64 decoding returns bytestrings
        decoded_value = value.decode("base64").decode("utf-8")
        return decoded_value
