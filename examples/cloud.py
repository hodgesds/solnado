from solnado import SolrClient
from tornado import ioloop

c = SolrClient()

def cb(reply):
    print reply.body
    ioloop.IOLoop.instance().stop()

c.status(callback=cb)

ioloop.IOLoop.instance().start()
