# -*- coding: utf-8 -*-
from excalibur.check import CheckACL, CheckArguments, CheckRequest, CheckSource
from excalibur.decode import DecodeArguments
from excalibur.loader import PluginLoader

def check_all(acl, sources, ressources, query):
    """
    check all yml
    """

    check_source = CheckSource(sources)
    check_source.check(query['source'], query['remote_ip'], query['signature'], query['arguments'])

    check_acl = CheckACL(acl)
    check_acl.check(query['source'], query['ressource'], query['method'])

    check_request = CheckRequest(ressources)
    check_request.check(query['request_method'], query['ressource'], query['method'], query['arguments'])

    decode_arguments = DecodeArguments(ressources)
    decode_arguments.decode(query['ressource'], query['method'], query['arguments'])

    check_arguments = CheckArguments(ressources)
    check_arguments.check(query['arguments'], query['ressource'], query['method'])


def run_plugins(plugins, query, plugin_module):
    """
    Parcours les plugins et execute la méthode demandée
    """

    data = {}
    errors = {}
    plugin_loader = PluginLoader(plugin_module)

    for plugin_name, parameters_sets in plugins.iteritems():
        for parameters_index, parameters in enumerate(parameters_sets):
            plugin = plugin_loader.get_plugin(plugin_name)
            plugin_data = None
            f_name = "%s_%s" % (query['ressource'], query['method']) # Name of the function to run
            if not hasattr(plugin, f_name):
                continue # Ressource/method not implemented in plugin
            try:
                f = getattr(plugin, f_name)
                plugin_data = f(parameters, query['arguments'])
            except Exception as e:
               errors[plugin_name] = {'source' : query['source'], 
                                      'ressource' : query['ressource'], 
                                      'method' : query['method'], 
                                      'arguments' : query['arguments'], 
                                      'parameters_index': parameters_index, 
                                      'error': e.__class__.__name__
                                      }


            if plugin_data is not None:
                data[plugin_name] = plugin_data

    return data, errors