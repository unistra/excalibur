import asyncio

class Plugin1(object):

    @asyncio.coroutine
    def actions_action1(self, parameters, query, future, raw_plugin_name, index):
        future.set_result(
            {"plugin_name": raw_plugin_name,
             'data':"p1ok1",
             'error':None}
        )


    @asyncio.coroutine
    def actions_action2(self, parameters, query, future, raw_plugin_name, index):

        e = Exception("error plugin 2 action 2 !")

        future.set_result(
            {"plugin_name": raw_plugin_name,
             'data': None,
             'error': { 'project': query.project,
                        'source': query.source,
                        'ressource': query.ressource,
                        'method': query.method,
                        'arguments': query.arguments,
                        'parameters_index': index,
                        'error': e.__class__.__name__,
                        'error_message': str(e)
                    }
                      
             }
        )
