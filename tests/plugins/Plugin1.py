import asyncio
from excalibur.core import Plugin

class Plugin1(Plugin):

    @asyncio.coroutine
    def actions_action1(self, parameters, future, raw_plugin_name, index):

        future.set_result(
            {"plugin_name": raw_plugin_name,
             'data':"p1ok1",
             'error':None}
        )


    @asyncio.coroutine
    def actions_action2(self, parameters, future, raw_plugin_name, index):

        e = Exception("error plugin 1 action 2 !")
        future.set_result(
            {"plugin_name": raw_plugin_name,
             'data': None,
             'error':  self.format_error(self.query,e,index)
                      
             }
        )
