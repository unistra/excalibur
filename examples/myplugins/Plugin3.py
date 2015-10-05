from excalibur.core import Plugin
import asyncio
import aiohttp

class Plugin3(Plugin):
    
    @asyncio.coroutine
    def website_get(self, parameters, future, raw_plugin_name, index):
        print(self.query.arguments["title"])
        r = yield from aiohttp.get(parameters['url'])
        r2 = yield from r.text()
        
        future.set_result(
            {"plugin_name": raw_plugin_name,
             'data':r2,
             'error':None}
        )
