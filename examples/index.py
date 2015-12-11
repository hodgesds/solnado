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

