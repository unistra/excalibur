=====
Usage
=====

Excalibur is a tool intended on ressources management in applications.

The purpose of Excalibur is to execute plugins methods according to query parameters.

Excalibur analyzes the query according to yaml configuration files and select which plugins should be run, and which parameters they should use,

dependending on the allowances set in the yaml files.

Excalibur works with Query and PluginsRunner objects which should be imported like : ::

	from excalibur.core import PluginsRunner, Query
	
associated error classes should be imported too : ::

	from excalibur.exceptions import ExcaliburClientError, ExcaliburInternalError
	



Required Parameters 
===================

For Query
---------

The Query contains the data required by the PluginsRunner to select which process the app should use. 

For example, if you use this app in a web project, you could have a route like : ::

	http://myapp.mydomain.com/project/source/ressource/method?sign=signature&firstname=toto&lastname=tata

- project :  The project specified in the sources.yml. Uses "default" by default.
- source : targeted source specified in the sources.yml.
			- 'all' is a reserved keyword, when you set source to all, 
			  excalibur launches all the plugins whose yaml carries the right api key,
			  NOT ALL PLUGINS BUT ALL ALLOWED PLUGINS. 
			- you can specify multiple sources, if so you have to separate them with ','
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

The client side sha1 signature is optional.

By passing check_signature=False at your PluginRunner initialization you can exempt the consumer from building the sha1.

It does not mean that the matching validation will be skipped, but that it will be made internally by Excalibur.



For PluginsRunner
---------

The PluginsRunner constructor signature takes for arguments the yml configuration files paths, the plugin module's name and query 

- acl_file : the acl file path.
- sources_file : the sources file path.
- ressources_file : the ressources file path.
- plugins_module : the plugins module's name.

The callable method need the following argument:

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
              	arguments=arguments,
                project="my_project"
              	)

	plugin_runner = PluginsRunner(acl_file,
                              sources_file,
                              ressources_file,
                              plugins_module)
    
    data, errors = plugin_runner(query)
    
- data is a dict which contains all plugins's data
- errors is a dict which contains all plugins's errors
                              
In a Django project it would differ a bit in that way : ::

	from django.conf import settings
	
	...
	
	plugin_runner = PluginsRunner(settings.EXCALIBUR_ACL_FILE,
                              settings.EXCALIBUR_SOURCES_FILE,
                              settings.EXCALIBUR_RESSOURCES_FILE,
                              settings.EXCALIBUR_PLUGINS_MODULE)
    ...


You can now use the collected data and/or errors as you see fit.

Tips
----
- You can use the sources_names method of the PluginsRunner to get all sources names by project. It can be useful to loop over it to make multiple queries.
- You can use the "raw_yaml_content=True" parameter for the PluginsRunner to pass a raw string instead of a file
- You can use the "check_ip=False" parameter for the PluginsRunner to allow all ips.