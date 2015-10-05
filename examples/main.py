"""
Run this file to test
"""

from excalibur.core import PluginsRunner, Query
from excalibur.exceptions import ExcaliburClientError, ExcaliburInternalError


if __name__ == "__main__":
    query = Query(source="test",
            remote_ip=None,
            signature=None,
            ressource="website",
            method="get",
            request_method="GET",
           arguments={"title": "Hello World"})

    plugin_runner = PluginsRunner("./acl.yml",
                              "./sources.yml",
                              "./ressources.yml",
                              "myplugins",
                              check_ip=False,
                              check_signature=False)

    data, errors = plugin_runner(query)

    print(data)
    print(errors)
