import json
from functools import partial
from nose.tools import ok_, eq_
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
    def test_core_status(self):
        res = yield gen.Task(partial(self.client.core_status))
        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)

    @gen_test(timeout=10)
    def test_core_create(self):
        # delete any cores with the name to be created
        #yield gen.Task(partial(self.client.core_unload, 'test', **{'del_inst_dir':'true'}))
        yield gen.Task(partial(self.client.core_unload, 'test'))

        res = yield gen.Task(partial(self.client.core_create, 'test'))
        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)

        # remove the created core
        yield gen.Task(partial(self.client.core_unload, 'test'))

    @gen_test(timeout=15)
    def test_core_reload(self):
        # delete any cores with the name to be created
        yield gen.Task(partial(self.client.core_unload, 'foo'))
        yield gen.Task(partial(self.client.core_create, 'foo'))

        res = yield gen.Task(partial(self.client.core_reload, 'foo'))
        ok_(json.loads(res.body.decode('utf8')))
        eq_(200, res.code)

        # remove the created core
        yield gen.Task(partial(self.client.core_unload, 'foo'))


