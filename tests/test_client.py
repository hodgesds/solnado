from tornado.testing import AsyncTestCase
from solnado import SolrClient


class ClientTestCase(AsyncTestCase):
    def test_mk_req(self):
        c = SolrClient()
        self.assertEquals(c.base_url, c.mk_req('').url)
        self.assertEquals('GET', c.mk_req('').method)

    def test_mk_url(self):
        c = SolrClient()
        url = c.mk_url(*['a','b','c'], **{'key':'value'})
        self.assertEquals('/a/b/c?key=value', url)

