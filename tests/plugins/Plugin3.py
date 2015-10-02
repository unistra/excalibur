import asyncio

class Plugin3(object):

    @asyncio.coroutine
    def actions_notexist(self, parameters, query, future, raw_plugin_name, index):
        future.set_result({"plugin_name": raw_plugin_name, 'data':None, 'error':None})