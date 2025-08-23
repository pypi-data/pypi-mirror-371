OSDU Command Line Interface
===========================

Command-line interface for interacting with OSDU.

NOTE: With version 0.0.45 and earlier the pip install command may need extra parameter since a dependency is not available from pypi.org:

.. code-block:: bash

    pip install osducli --extra-index-url=https://community.opengroup.org/api/v4/projects/148/packages/pypi/simple


Usage
=====

The first time you use the CLI you should run the configure command to provide connection information and other important configuration.

.. code-block:: bash

  osdu config update

Once configured use the CLI as shown below. Omitting a command will display a list of available options.

.. code-block:: bash

  osdu <command>

For more information, specify the `-h` flag:

.. code-block:: bash

  osdu -h
  osdu <command> -h

Change Log
==========

0.0.46
------
- Simpler install command without extra-index-url
- Fix error handling to get correct message details

0.0.45
------

- Fix msal_non_interactive authentication

0.0.44
------

- Fix handling of json data in put and post requests

0.0.43
------

- Fix storage add command
- Implement storage add batching

0.0.42
------

- Simplify configuration for AWS
- Fix storage get command

0.0.41
------

- Use common OSDU SDK
- In addition to Azure, support OSDU implementations on AWS, GC, IBM and Bare Metal
- Added Wellbore DDMS commands
- Added file metadata command

0.0.39
------

- Support python 3.12 and 3.13, drop older versions
- Simplify config handling
- Fix status command

0.0.38
------

- msal non interactive auth added
- updated imported packages
- Support python 3.11, drop support for python 3.8

0.0.37
------

- fix for crash when workflow status result didn't contain an endTimeStamp
- fix dataload ingest --batch option should work as flag and with specified batch size

0.0.36
------

- Added entitlements members groups command

0.0.35
------

- Split storage get to storage list (for id's) and storage get (for records)
- storage get --id option added

0.0.34
------

- Bump sdk version to 0.0.12
- Added legal add and delete commands
- Fix entitlements add group error
- Add description option to entitlements add group

0.0.33
------

- fix storage delete returns 204 error when deleted successfully

0.0.32
------

- dataload ingest added options for passing legal tags and acl
- correct CRS Converter Service naming
 
0.0.31
------

- Added update check when running 'osdu' or 'osdu version'

0.0.30
------

- API documentation pages are shown in info commands
- workflow get, runs and status commands

0.0.29
------

- storage commands

0.0.28
------

- search kind command
- search id supports limit
- search query supports a specific query
- global query option renamed to filter

0.0.27
------

- file download and info commands
  
0.0.26
------

- crs transforms command

0.0.25
------

- test against python 3.10 in addition to 3.8, 3.9
- crs commands

0.0.24
------

- checkrefs authority, acl and legal parameters for generated files

0.0.23
------

- osdu version shows service versions
- added info subcommand to entitlements, legal, schema, search, unit, workflow.

0.0.22
------

- search query supports limit

0.0.21
------

- dataload verify supports reference-data {{NAMESPACE}} replacement

0.0.20
------

- dataload support sequence file for ordered loading (ref. standard reference-data)
 
0.0.19
------

- schema add --overwrite-existing option
- merge dataload checkrefs code (wip)
- user friendly output mode
- improved dataload helper text
- support for python 3.10

0.0.18
------

- split global options in help text for clarity
- search table output fields changed

0.0.17
------

- change osducli references to osdu

0.0.16
------

- fix ingestion batch sizes
  
0.0.15
------

- *entitlements members add* - added role option
- *entitlements members remove* command added

0.0.14
------
- callable as osdu instead of osducli
- search query & search id commands
- dataload ingest --skip-existing option
- Add legal service and list tags
  
0.0.13
------

- workflow register / unregister commands
- dataload ingest - wait and simulate options

0.0.12
------

- Fix config permissions

0.0.11
------

- schema commands
- dataload batching imporvements

0.0.10
------

- refeactor code to use click instead of knack

0.0.9
-----

- entitlements commands

0.0.8
-----

- use osdu-sdk 0.0.2
  
0.0.7
-----

- Uses osdu-sdk for backend code
  
0.0.6
-----

- Refactor of connection code

0.0.3
-----

- Bulk upload commands (file upload still missing)
- Interactive login
- Config improvements
- Additional testing

0.0.2
-----

- Cleanup and diverse fixes
  
0.0.1
-----

- Initial release.
