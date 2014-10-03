# -*- coding: utf-8 -*-
"""
Cross-classes utils
"""
import hashlib
import traceback
import re

ALL_KEYWORD = "all"
PLUGIN_NAME_SEPARATOR = "|"
SOURCE_SEPARATOR = ","


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


def sources_list_or_list(source):
    """
    """
    return list(source.split(SOURCE_SEPARATOR)) if\
        SOURCE_SEPARATOR in source else [source]


def all_sources_or_sources_list_or_list(source, sources):
    """
    """
    return list(sources.keys())\
        if source == ALL_KEYWORD else sources_list_or_list(source)


def is_simple_request(source, sources):
    """
    """
    return source != ALL_KEYWORD and\
        SOURCE_SEPARATOR not in source


def is_simple_request_and_source_not_found(source, sources):
    """
    """
    return is_simple_request(source, sources) and source not in sources.keys()


def ip_found_in_sources(source, sources, request_ip):
    """
    """
    ip_authorized = True

    targeted_sources = []
    if is_simple_request(source, sources):
        targeted_sources = [sources[source].get('ip',[])]
    else:
        targeted_sources = [it["ip"] for
                            it in sources.values() if "ip" in
                            list(it.keys())]
    for ip_list in targeted_sources:
        if not [ip for ip in ip_list if re.match(ip, request_ip)]:
            ip_authorized = False
    return ip_authorized 


def get_api_keys_by_sources(sources, targets):
    """
    """
    def get_keys(x):
        if type(sources[x]["apikey"]) is list:
            return sources[x]["apikey"]
        else:
            return[sources[x]["apikey"]]

    return {target: get_keys(target) for target in targets}
