# -*- coding: utf-8 -*-
from excalibur.check import CheckACL, CheckArguments, CheckRequest, CheckSource
from excalibur.decode import DecodeArguments
from excalibur.loader import PluginLoader

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


def run_plugins(plugins, ressource, method, arguments, source, plugin_module):
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
            f_name = "%s_%s" % (ressource, method) # Name of the function to run
            if not hasattr(plugin, f_name):
                continue # Ressource/method not implemented in plugin
            try:
                f = getattr(plugin, f_name)
                plugin_data = f(parameters, arguments)
            except Exception as e:
               errors[plugin_name] = {'source' : source, 
                                      'ressource' : ressource, 
                                      'method' : method, 
                                      'arguments' : arguments, 
                                      'parameters_index': parameters_index, 
                                      'error': e.__class__.__name__
                                      }


            if plugin_data is not None:
                data[plugin_name] = plugin_data

    return data, errors