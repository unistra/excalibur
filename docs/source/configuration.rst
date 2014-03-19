=============
Configuration
=============

Toutes les configurations de cette librairie seront réalisées via des fichiers yaml.


sources.yml
===========

Paramétrage de l'api et des plugins en fonction des établissements.

Exemple : ::

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


On peut également rajouter un niveau supérieur par projet si besoin.

Exemple : ::

	project1:
	    etab1:
	        ...

	    etab2:
	        ...

	project2:
	    etab1:
	        ...


ressources.yml
==============

Description des méthodes et des arguments en fonction des établissements.

Exemple : ::

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

    ...


acl.yml
=======

Liste des méthodes autorisées en fonction des établissements.

Exemple : ::

	uds:
		user:
			- setpassword
			- deactivate
			- archive
	ensas:
		user:
			- setpassword

On peut également rajouter un niveau supérieur par projet si besoin.

Exemple : ::

	project1:
	    etab1:
	        actions:
	            - action1
	            - action2

	    etab2:
	        actions:
	            - action1

	project2:
	    etab1:
	        actions:
	            - action1
	            - action2


module plugins
==============

Un module réservé aux plugins doit être présent dans votre application.

Celui-ci sera présenté de la manière suivante : ::

	plugins
		Plugin1.py
		Plugin2.py
		Plugin3.py

Chaque fichier doit contenir une classe du même nom.
Cette classe doit contenir les méthodes disponibles décrits dans les fichiers de configuration précédents.
Ces méthodes doivent prendre comme arguments "parameters" et "arguments" et peuvent retourner des données.

Exemple : ::

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


Dans un projet django
=====================

Dans le settings.py de votre projet django, il faudra définir les chemins de vos fichiers yaml et le chemin du module de plugins de la manière suivante :

TODO