Tornado Solr Client
-------------------

Tornado http client for Solr 5.X.X.

Documentation
-------------
http://solnado.readthedocs.org/en/latest/

Example
-------
Creating a collection and adding a document:

.. code-block:: python

    from functools import partial
    from solnado   import SolrClient
    from tornado   import ioloop, gen
    
    c = SolrClient()
    
    @gen.coroutine
    def create_core():
        p = partial(
            c.core_create,
            'foo',
        )
        res = yield gen.Task(p)
        raise gen.Return(res)
    
    @gen.coroutine
    def create_collection():
        p = partial(
            c.create_collection,
            'foo',
        )
        res = yield gen.Task(p)
        raise gen.Return(res)

    @gen.coroutine
    def index_documents(docs):
        p = partial(
           c.add_json_documents,
           'foo',
           docs,
           **{'commitWithin': 0}
        )
        res = yield gen.Task(p)
        raise gen.Return(res)

    @gen.coroutine
    def main_coro():
        yield create_core()
        yield create_collection()
        res = yield index_documents([
            {
                'id':'123',
                'Title': 'A tale of two documents',
            },{
                'id': '456',
                'Title': 'It was the best of times',
        }])
    
        print res.body, res.code
    
    
    ioloop.IOLoop.instance().run_sync(main_coro)


CLI
---
Solnado provides a simple to use API to interact with Solr.

Use the following environment variables:

.. code-block:: bash

    export SOLR_HOST=localhost
    export SOLR_PORT=8983


To get the current solr status:

.. code-block:: bash

    solnado status


Create a collection:

.. code-block:: bash

    solnado collection create foo

Delete a collection:

.. code-block:: bash

    solnado collection delete foo


Query a collection

.. code-block:: bash

    solnado search foo "*"

Create a core:

.. code-block:: bash

    solnado core create foo


Delete a core:

.. code-block:: bash

    solnado core delete foo


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



