import json
from functools import partial
from nose.tools import ok_, eq_, nottest
from solnado import SolrClient
from tornado import gen
from tornado.testing import AsyncTestCase, gen_test


class ClientTestCase(AsyncTestCase):
    def setUp(self):
        super(ClientTestCase, self).setUp()
        self.client = SolrClient()

    def test_mk_req(self):
        self.assertEquals(self.client.base_url, self.client.mk_req('').url)
        self.assertEquals('GET', self.client.mk_req('').method)

    def test_mk_url(self):
        url = self.client.mk_url(*['a','b','c'], **{'key':'value'})
        self.assertEquals('/a/b/c?key=value', url)

    @gen_test(timeout=10)
    def test_create_collection(self):
        p = partial(self.client.create_collection, 'fox', **{'collection_kwargs':{'numShards':1}})
        res = yield gen.Task(p)
        eq_(200, res.code)
        p = partial(self.client.delete_collection, 'fox')
        yield gen.Task(p)

    @gen_test(timeout=10)
    def test_core_status(self):
        res = yield gen.Task(partial(self.client.core_status))
        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)

    @gen_test(timeout=10)
    def test_core_create(self):
        res = yield gen.Task(partial(self.client.core_create, 'test'))
        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)

        yield gen.Task(partial(self.client.core_unload, 'test'))
        yield gen.Task(partial(self.client.core_reload, 'test'))

    @gen_test(timeout=15)
    def test_core_reload(self):
        yield gen.Task(partial(self.client.core_create, 't'))
        res = yield gen.Task(partial(self.client.core_reload, 't'))

        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)

        yield gen.Task(partial(self.client.core_unload, 't'))
        yield gen.Task(partial(self.client.core_reload, 't'))

    #@gen_test(timeout=25)
    #def test_core_rename(self):
    #    yield gen.Task(partial(self.client.core_create, 'baz'))
    #    yield gen.Task(partial(self.client.core_reload, 'baz'))

    #    res = yield gen.Task(partial(self.client.core_rename, 'baz', 'qux'))
    #    eq_(200, res.code)
    #    print(res.body)

    #    yield gen.Task(partial(self.client.core_reload, 'baz'))
    #    yield gen.Task(partial(self.client.core_reload, 'qux'))
    #    yield gen.Task(partial(self.client.core_unload, 'qux'))
    #    yield gen.Task(partial(self.client.core_reload, 'qux'))

    @gen_test
    def test_add_json_document(self):
        d = {"id":"123", "title":"test_add"}
        yield gen.Task(partial(self.client.core_create, 'add_j'))
        yield gen.Task(partial(self.client.core_reload, 'add_j'))

        res = yield gen.Task(partial(self.client.add_json_document, 'add_j', d))

        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)
