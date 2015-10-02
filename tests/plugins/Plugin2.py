import asyncio
from excalibur.core import Plugin


class Plugin2(Plugin):

    @asyncio.coroutine
    def actions_action1(self, parameters, future, raw_plugin_name, index):
        future.set_result(
            {"plugin_name": raw_plugin_name,
             'data':"p2ok1",
             'error':None})

    @asyncio.coroutine
    def actions_action2(self, parameters, future, raw_plugin_name, index):
        e = Exception("error plugin 2 action 2 !")
        future.set_result(
            {"plugin_name": raw_plugin_name,
             'data': None,
             'error':{ 'project': self.query.project,
                        'source': self.query.source,
                        'ressource': self.query.ressource,
                        'method': self.query.method,
                        'arguments': self.query.arguments,
                        'parameters_index': index,
                        'error': e.__class__.__name__,
                        'error_message': str(e)
                    }
             }
        )
