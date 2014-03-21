=====
Usage
=====

The purpose of Excalibur is to execute plugins methods according to query parameters.
Excalibur analyzes the query according to yaml configuration files and select which plugin to run.

Excalibur works with Query and PluginsRunner objects which should be imported like : ::

	from excalibur.core import PluginsRunner, Query
	
associated error classes should be imported too : ::

	from excalibur.exceptions import ExcaliburClientError, ExcaliburInternalError
	



Required Parameters 
===================

For Query
---------

The Query contains the data required by the PluginsRunner to select which process the app should select. 

For example, if you use this app in a web project, you could have a route like : ::

	http://myapp.mydomain.com/project/source/ressource/method?sign=signature&firstname=toto&lastname=tata

- project : optional param. The project specified in the sources.yml.
- source : targeted source specified in the sources.yml.
- remote_ip : the ip address of the client.
- signature : passed in the query string, sha1 encoded. See above for more details.
- ressource : targeted ressource specified in the .yml.
- method : specified in the yaml ressources, match the plugin class method.
- request_method : GET, POST, PATCH, PUT or DELETE
- arguments : a dict of key/values (contains firstname, lastname, ...)
 
Specs of the signature
----------------------
 
The signature is a sha1 hash obtained by:
    - concatenation of, in that order :
        - the client apikey found in the sources.yml
        - the first arg key
        - the first arg value
        - second arg key
        - second arg value
        - etc ...

    - hash to sha1

    Example:
        - project: project
        - source : source
        - apikey: "0XFF"
        - firstname: "toto"
        - lastname=tata

        concatenated string is:
        "0XFFfirstnametotolastnametata"

        hash is then :
        "337730197d2aae0a0c3ce9eeea00554beb313ad4"

        called url is:
        http://myapp.mydomain.com/project/source/ressource/method?sign=337730197d2aae0a0c3ce9eeea00554beb313ad4&firstname=toto&lastname=tata



For PluginsRunner
---------

The PluginsRunner constructor signature takes for arguments the yml configuration files paths, the plugin module's name and query 

- acl_file : the acl file path.
- sources_file : the sources file path.
- ressources_file : the ressources file path.
- plugins_module : the plugins module's name.
- query : the query object.

How to
======

In your code you could, for instance, write : ::

	from excalibur.core import PluginsRunner, Query
	from excalibur.exceptions import ExcaliburClientError, ExcaliburInternalError

	query = Query(source=source, 
              	remote_ip=remote_ip,
              	signature=signature,  
              	ressource=ressource,  
              	method=method,   
              	request_method=request_method,  
              	arguments=arguments)

	plugin_runner = PluginsRunner(acl_file,
                              sources_file,
                              ressources_file,
                              plugins_module, 
                              query)
    
    data, errors = plugin_runner()
    
- data is a dict which contains all plugins's data
- errors is a dict which contains all plugins's errors
                              
In a Django project it would differ a bit in that way : ::

	from django.conf import settings
	
	...
	
	plugin_runner = PluginsRunner(settings.EXCALIBUR_ACL_FILE,
                              settings.EXCALIBUR_SOURCES_FILE,
                              settings.EXCALIBUR_RESSOURCES_FILE,
                              settings.EXCALIBUR_PLUGINS_MODULE, 
                              query)
    ...


You can now use the collected data and/or errors as you see fit.                  