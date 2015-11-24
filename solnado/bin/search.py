from __future__ import print_function
from functools import partial
from tornado import gen
from tornado import ioloop
from solnado.client import SolrClient
import os

def solnado_cmd(subparsers):
    query_subparser = subparsers.add_parser('search')
    query_subparser.set_defaults(func=main)
    query_subparser.add_argument(
        '--host',
        default = os.environ.get('SOLR_HOST','localhost'),
        help    = 'Solr server',
    )
    query_subparser.add_argument(
        '-p', '--port',
        default = os.environ.get('SOLR_PORT', 8983),
        type    = int,
    )
    query_subparser.add_argument(
        'collection',
        help = 'collection to query',
    )
    query_subparser.add_argument(
        'query',
        help = 'query'
    )
    query_subparser.add_argument(
        '-f', '--filter',
        nargs   = '+',
        default = None,
    )
    query_subparser.add_argument(
        '-l', '--limit',
        type    = int,
        default = None,
    )

@gen.coroutine
def main_coro(args):
    c = SolrClient(host=args.host)
    q = {'q': args.query}

    if args.filter:
        q.update({'json.filter': args.filter})
    if args.limit:
        q.update({'json.limit': args.limit})

    p = partial(c.query, args.collection, q)
    s = yield gen.Task(p)
    print(s.body)

def main(args):
    m = partial(main_coro, args)
    ioloop.IOLoop.current().run_sync(m)
