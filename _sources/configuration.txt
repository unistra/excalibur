=============
Configuration
=============

All settings directives are done by yaml files.
This is where you specify which process Excalibur should call, which way it should do it, depending on who asks it.


sources.yml
===========

WARNING : 'all' and ',' are reserved in the Excalibur syntax, don't use them as sources names.


Api configuration by sources.

Each source can have an apikey entry, which will be matched against the 
apikey carried by the request.

 
Multiple apikeys can be registered by setting the value of this entry
to a list.

The ip entry works the same way, and is used to determine which ips are authorized.

A single request can target one or many sources. 

When building the request, to target multiple establishments
you should use "," as separator, in the following example it would thus be source="uds,ensas".

You can also
set the source to "all" in the request, in which case the PluginRunner will return all the sources where your credentials 
are found.

The parameters with which each plugin is to be executed depending on the user requiring it are registered here.

Example : ::

	uds:
		apikey: S3CR3T
		ip:
			- 127.0.0.1
			- X.X.X.X

		plugins:
			Ldap:
				-	url: ldaps://ldap1.domaine.fr:636
					binddn: S3CR3T
					password: S3CR3T
					basedn: ou=users
					password method: [userPassword, sambaLMPassword, sambaNTPassword]
					login attribute: uid

				-	url: ldaps://ldap2.domaine.fr:636
					binddn: S3CR3T
					password: S3CR3T
					basedn: ou=users
					password method: [unicodePwd]
					login attribute: sAMAccountName

			Kerberos:
				-	spn: S3CR3T
					keytabfile: "file.keytab"
					kinit_command: "/usr/bin/kinit"
					kadmin_command: "/usr/sbin/kadmin"

			Process:
				-	path: /path/script_webmail.sh
					user_deactivate_parameters: [login, ]

			Ldapuds:
				-	spore: http://ldapws.domaine.fr/description.json
					token: S3CR3T

			Aduds:
				-	spore: http://aduds.domaine.fr/description.json
					token: S3CR3T
					deactivation_code: 66050
					delete_info: delete

	ensas:
		...


A further level can be set in order to manage sources by projects.

Example : ::

	project1:
	    source1:
	        ...

	    source2:
	        ...

	project2:
	    source1:
	        ...


ressources.yml
==============


Methods and arguments descriptions by sources.
The registered keys found under the "arguments" entry are the the request arguments for
which validations will be made. If you want a validation to be optional, i.e to be runned 
only if the the argument is present, you can set optional to true at the same level than the
check.

Example : ::

	user:
		setpassword:
			request method: GET
			arguments:
				login:
					checks:
						min_length: 2
						max_length: 50
				password:
					checks:
						min_length: 8
						max_length: 50
					encoding: base64
				first_name:
				       checks:
						min_length: 8
						max_length: 50
					optional:true
					

    ...


acl.yml
=======

List of allowed methods by sources. This module is used by the PluginRunner for validation purposes.
On receiving the request it ensures that the plugins it targets contain the methods that are going to be 
called by the request.

Example : ::

	uds:
		user:
			- setpassword
			- deactivate
			- archive
	ensas:
		user:
			- setpassword

A further level can be specified to manage sources by project.

Example : ::

	project1:
	    source1:
	        actions:
	            - action1
	            - action2

	    source2:
	        actions:
	            - action1

	project2:
	    source1:
	        actions:
	            - action1
	            - action2


plugins module
==============

A private module dedicated to plugins must be present in your app.

It should conform to the following format : ::

	plugins
		Plugin1.py
		Plugin2.py
		Plugin3.py

Each plugin class must be contained in an homonymous .py.
This class must contain all the methods that the yml description files describe as available.
Those methods signatures should at least be able to take as arguments "parameters" and "arguments", their return type is up to you.

Example : ::

	class Plugin1(object) :

		def user_deactivate(self, parameters, arguments):
			...
			return data

		def user_archive(self, parameters, arguments):
			...
			return data

		def user_setpassword(self, parameters, arguments):
			...
			return data


In a Django project
===================

In your django project's settings.py, the yaml file paths and the plugins module's name should be specified, for instance : ::

	from os.path import abspath, basename, dirname, join, normpath

	SETTINGS_ROOT = dirname(abspath(__file__))
	
	EXCALIBUR_SOURCES_FILE = join(SETTINGS_ROOT, "sources.yml")
	EXCALIBUR_RESSOURCES_FILE = join(SETTINGS_ROOT, "ressources.yml")
	EXCALIBUR_ACL_FILE = join(SETTINGS_ROOT, "acl.yml")
	EXCALIBUR_PLUGINS_MODULE = "yourproject.yourapp.plugins"