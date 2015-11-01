from solnado import SolrClient
from tornado import ioloop

c = SolrClient()

def cb(reply):
    print reply.body
    ioloop.IOLoop.instance().stop()

c.core_status(callback=cb)

ioloop.IOLoop.instance().start()
