Tornado Solr Client
===================

Tornado http client for Solr 5.X.X.

CLI
---
Solnado provides a simple to use API to interact with Solr.

Use the following environment variables:

    export SOLR_HOST=localhost
    export SOLR_PORT=8983

To get the current solr status:

    solnado status

Create a collection:

    solnado collection create foo

Delete a collection:

    solnado collection create foo

Query a collection

    solnado search foo "*"

License
-------

Copyright 2015 Daniel Hodges

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Testing
-------
Tested with python:
2.6, 2.7, 3.2, 3.3, 3.4, 3.5 and pypy


Build status
------------
.. image:: https://travis-ci.org/hodgesds/solnado.svg?branch=master
    :target: https://travis-ci.org/hodgesds/solnado

Documentation
-------------
http://solnado.readthedocs.org/en/latest/


