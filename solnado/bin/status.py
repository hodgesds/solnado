from __future__ import print_function
from functools import partial
from tornado import gen
from tornado import ioloop
from solnado.client import SolrClient
import os

def solnado_cmd(subparsers):
    status_subparser = subparsers.add_parser('status')
    status_subparser.set_defaults(func=main)
    status_subparser.add_argument(
        '--host',
        default = os.environ.get('SOLR_HOST','localhost'),
        help    = 'Solr server',
    )
    status_subparser.add_argument(
        '-p', '--port',
        default = os.environ.get('SOLR_PORT', 8983),
        type    = int,
    )

@gen.coroutine
def main_coro(args):
    c = SolrClient(host=args.host)
    s = yield gen.Task(c.core_status)
    print(s.body)

def main(args):
    m = partial(main_coro, args)
    ioloop.IOLoop.current().run_sync(m)
