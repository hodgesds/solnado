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

    @gen_test(timeout=30)
    def test_create_collection(self):
        p = partial(self.client.create_collection, 'fox', **{'collection_kwargs':{'numShards':1}})
        res = yield gen.Task(p)
        eq_(200, res.code)
        p = partial(self.client.delete_collection, 'fox')
        yield gen.Task(p)

    @gen_test(timeout=30)
    def test_core_status(self):
        res = yield gen.Task(partial(self.client.core_status))
        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)

    @gen_test(timeout=30)
    def test_core_create(self):
        yield gen.Task(partial(self.client.core_unload, 'test_core'))
        res = yield gen.Task(partial(self.client.core_create, 'test_core'))
        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)

        yield gen.Task(partial(self.client.core_unload, 'test_core'))
        yield gen.Task(partial(self.client.core_reload, 'test_core'))

    @gen_test(timeout=30)
    def test_core_reload(self):
        yield gen.Task(partial(self.client.core_create, 't'))
        res = yield gen.Task(partial(self.client.core_reload, 't'))

        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)

        unload = yield gen.Task(partial(self.client.core_unload, 't'))
        eq_(200, unload.code)
        yield gen.Task(partial(self.client.core_reload, 't'))

    #@gen_test(timeout=25)
    #def test_core_rename(self):
    #    yield gen.Task(partial(self.client.core_create, 'baz'))
    #    yield gen.Task(partial(self.client.core_reload, 'baz'))

    #    res = yield gen.Task(partial(self.client.core_rename, 'baz', 'qux'))
    #    eq_(200, res.code)

    #    yield gen.Task(partial(self.client.core_reload, 'baz'))
    #    yield gen.Task(partial(self.client.core_reload, 'qux'))
    #    yield gen.Task(partial(self.client.core_unload, 'qux'))
    #    yield gen.Task(partial(self.client.core_reload, 'qux'))

    @gen_test(timeout=30)
    def test_add_json_document(self):
        d = {"id":"123", "title":"test_add"}
        yield gen.Task(partial(self.client.core_create, 'add_j'))
        yield gen.Task(partial(self.client.core_reload, 'add_j'))

        res = yield gen.Task(partial(self.client.add_json_document, 'add_j', d))

        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)

    @gen_test(timeout=30)
    def test_add_json_documents(self):
        d = [
            {"id":"123", "title":"test_add"},
            {"id":"456", "title":"bar_baz"},
        ]
        yield gen.Task(partial(self.client.core_create, 'add_docs'))
        yield gen.Task(partial(self.client.core_reload, 'add_docs'))

        res = yield gen.Task(partial(self.client.add_json_document, 'add_docs', d))

        eq_(200, res.code)

    @gen_test(timeout=30)
    def test_query(self):
        d = [
            {"id":"123", "title":"test_add"},
            {"id":"456", "title":"bar_baz"},
        ]
        yield gen.Task(partial(self.client.core_create, 'add_docs'))
        yield gen.Task(partial(self.client.core_reload, 'add_docs'))

        yield gen.Task(partial(self.client.add_json_document, 'add_docs', d))

        q = {'q':'bar_baz'}
        res = yield gen.Task(partial(self.client.query, 'add_docs', q))
        eq_(200, res.code)

    @gen_test(timeout=30)
    def test_delete(self):
        yield gen.Task(partial(self.client.delete_collection, 'qux'))
        yield gen.Task(partial(self.client.create_collection, 'qux'))
        d = [
            {"id":"123", "title":"test_add"},
            {"id":"456", "title":"bar_baz"},
        ]
        yield gen.Task(partial(self.client.add_json_document, 'add_docs', d))
        res = yield gen.Task(partial(self.client.delete, 'qux', ['123']))
        eq_(200, res.code)
        yield gen.Task(partial(self.client.delete_collection, 'qux'))

    @gen_test(timeout=30)
    def test_create_collection(self):
        yield gen.Task(partial(self.client.delete_collection, 'qux'))
        res = yield gen.Task(partial(self.client.create_collection, 'qux'))
        eq_(200, res.code)

    @gen_test(timeout=30)
    def test_delete_collection(self):
        yield gen.Task(partial(self.client.delete_collection, 'bix'))
        yield gen.Task(partial(self.client.create_collection, 'bix'))
        res = yield gen.Task(partial(self.client.delete_collection, 'bix'))
        eq_(200, res.code)

    @gen_test(timeout=30)
    def test_reload_collection(self):
        yield gen.Task(partial(self.client.create_collection, 'qux'))
        res = yield gen.Task(partial(self.client.reload_collection, 'qux'))
        eq_(200, res.code)
        yield gen.Task(partial(self.client.delete_collection, 'qux'))

    @gen_test(timeout=30)
    def test_alias_collection(self):
        yield gen.Task(partial(self.client.delete_collection, 'bix'))
        yield gen.Task(partial(self.client.create_collection, 'bix'))
        res = yield gen.Task(partial(self.client.alias_collection, ['bix'], 'quix'))
        eq_(200, res.code)
        yield gen.Task(partial(self.client.delete_collection, 'bix'))

    @gen_test(timeout=30)
    def test_delete_alias_collection(self):
        yield gen.Task(partial(self.client.delete_collection, 'bix'))
        yield gen.Task(partial(self.client.create_collection, 'bix'))
        yield gen.Task(partial(self.client.alias_collection, ['bix'], 'quix'))
        res = yield gen.Task(partial(self.client.delete_alias_collection, 'quix'))
        eq_(200, res.code)
        yield gen.Task(partial(self.client.delete_collection, 'bix'))

    @gen_test(timeout=30)
    def test_add_field(self):
        yield gen.Task(partial(self.client.delete_collection, 'bix'))
        yield gen.Task(partial(self.client.create_collection, 'bix'))
        res = yield gen.Task(partial(self.client.add_field, 'bix', 'stamp', 'tdate'))
        eq_(200, res.code)
        yield gen.Task(partial(self.client.delete_collection, 'bix'))

    @gen_test(timeout=30)
    def test_delete_field(self):
        yield gen.Task(partial(self.client.delete_collection, 'bix'))
        yield gen.Task(partial(self.client.create_collection, 'bix'))
        yield gen.Task(partial(self.client.add_field, 'bix', 'stamp', 'tdate'))
        res = yield gen.Task(partial(self.client.delete_field, 'bix', 'stamp'))
        eq_(200, res.code)
        yield gen.Task(partial(self.client.delete_collection, 'bix'))

    @gen_test(timeout=30)
    def test_replace_field(self):
        yield gen.Task(partial(self.client.delete_collection, 'bix'))
        yield gen.Task(partial(self.client.create_collection, 'bix'))
        yield gen.Task(partial(self.client.add_field, 'bix', 'stamp', 'tdate'))
        res = yield gen.Task(partial(
            self.client.replace_field, 'bix', 'stamp',
            field_kwargs = {'type':'date'}
        ))
        eq_(200, res.code)
        yield gen.Task(partial(self.client.delete_collection, 'bix'))

    @gen_test(timeout=30)
    def test_add_dynamic_field(self):
        yield gen.Task(partial(self.client.delete_collection, 'bix'))
        yield gen.Task(partial(self.client.create_collection, 'bix'))
        res = yield gen.Task(
            partial(self.client.add_dynamic_field, 'bix', '*_s', 'string')
        )
        eq_(200, res.code)
        yield gen.Task(partial(self.client.delete_collection, 'bix'))
