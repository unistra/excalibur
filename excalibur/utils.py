# -*- coding: utf-8 -*-
"""
Cross-classes utils
"""
import hashlib


def add_args_then_encode(x, y, arguments):
    """
    sha1checks are made on aggregated Strings. The process is used
    in two spots. When checks regarding the sources.yml file are done
    and in the case where allowed sources cannot be deduced from query
    arguments but must be be obtained by checking apikeys directly in all 
    sources.
    """
    def add_args(x, args):
        """
        add arguments to main key before encoding
        """
        for argument in args:
            x += (argument + arguments[argument])
        return x

    def encode(x):
        """
        encode full string
        """
        return hashlib.sha1(x.encode("utf-8")).hexdigest()
    return encode(add_args(x, y))


def get_api_keys(entries, arguments):
    """
    """
    keys = []
    api_keys = []
    for entry in entries:
        if type(entry['apikey']) is list:
            for k in entry['apikey']:
                keys.append(k)
        elif type(entry['apikey']) is str:
            keys.append(entry['apikey'])

    if len(keys) > 1:
        for key in keys:
            api_keys += [add_args_then_encode(key,
                                              sorted(arguments),
                                              arguments) for entry in entries]
    else:
        api_keys = [add_args_then_encode(entry['apikey'] if 'apikey'
                                         in entry else '',
                                         sorted(arguments),
                                         arguments) for entry in entries]
    return api_keys
