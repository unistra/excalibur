import asyncio
from excalibur.core import Plugin


class Plugin3(Plugin):
    @asyncio.coroutine
    def actions_notexist(self, parameters, future, raw_plugin_name, index):
        future.set_result({"plugin_name": raw_plugin_name, 'data':None, 'error':None})
