# -*- coding: utf-8 -*-
from excalibur.check import CheckACL, CheckArguments, CheckRequest, CheckSource
from excalibur.decode import DecodeArguments

def check_all(acl, sources, ressources, request_method, source, ressource, method, remote_ip, arguments, signature):
    """
    check all yml
    """

    check_source = CheckSource(sources)
    check_source.check(source, remote_ip, signature, arguments)

    check_acl = CheckACL(acl)
    check_acl.check(source, ressource, method)

    check_request = CheckRequest(ressources)
    check_request.check(request_method, ressource, method, arguments)

    decode_arguments = DecodeArguments(ressources)
    decode_arguments.decode(ressource, method, arguments)

    check_arguments = CheckArguments(ressources)
    check_arguments.check(arguments, ressource, method)

