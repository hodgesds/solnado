from __future__ import print_function
from functools import partial
from tornado import gen
from tornado import ioloop
from solnado.client import SolrClient
import os

def solnado_cmd(subparsers):
    index_subparser = subparsers.add_parser('collection')
    sub = index_subparser.add_subparsers()
    add_create_subparser(sub)
    add_delete_subparser(sub)

def add_create_subparser(subparsers):
    create_subparser = subparsers.add_parser('create')
    create_subparser.set_defaults(func=create_collection)
    create_subparser.add_argument(
        '--host',
        default = os.environ.get('SOLR_HOST','localhost'),
        help    = 'Solr server',
    )
    create_subparser.add_argument(
        '-p', '--port',
        default = os.environ.get('SOLR_PORT', 8983),
        type    = int,
    )
    create_subparser.add_argument(
        '-r', '--router',
        choices = ['compositeId', 'implicit'],
        default = 'compositeId',
    )
    create_subparser.add_argument(
        'name',
        help = 'Collection name'
    )
    create_subparser.add_argument(
        '--replication',
        default = 1,
        type    = int,
        help    = 'replication factor',
    )
    create_subparser.add_argument(
        '-s', '--shards',
        dest    = 'shards',
        nargs   = '+',
        default = None,
        help    = 'Shard names',
    )
    create_subparser.add_argument(
        '-n', '--num-shards',
        dest    = 'nshards',
        type    = int,
        default = 1,
    )
    create_subparser.add_argument(
        '-m', '--max-shards',
        type    = int,
        default = 1,
    )

@gen.coroutine
def create_coro(args):
    c = SolrClient(host=args.host)
    collection_kwargs = {}

    if args.nshards and args.router == 'compositeId':
        collection_kwargs.update({'numShards': args.nshards})

    p = partial(
        c.create_collection,
        args.name,
        **{
            'replication':       args.replication,
            'router_name':       args.router,
            'shards':            args.shards,
            'shards_per_node':   args.nshards,
            'collection_kwargs': collection_kwargs,
        }
    )
    s = yield gen.Task(p)
    print(s.body)

def create_collection(args):
    c = partial(create_coro, args)
    ioloop.IOLoop.current().run_sync(c)

def add_delete_subparser(subparsers):
    delete_subparser = subparsers.add_parser('delete')
    delete_subparser.set_defaults(func=delete_collection)
    delete_subparser.add_argument(
        '--host',
        default = os.environ.get('SOLR_HOST','localhost'),
        help    = 'Solr server',
    )
    delete_subparser.add_argument(
        '-p', '--port',
        default = os.environ.get('SOLR_PORT', 8983),
        type    = int,
    )
    delete_subparser.add_argument(
        'name',
        help = 'Collection name'
    )
    delete_subparser.add_argument(
        '-s', '--shard',
        dest    = 'shard',
        default = None,
        help    = 'Shard to delete',
    )

@gen.coroutine
def delete_coro(args):
    c = SolrClient(host=args.host)

    p = partial(
        c.delete_collection,
        args.name,
        **{'shard': args.shard}
    )
    s = yield gen.Task(p)
    print(s.body)

def delete_collection(args):
    c = partial(delete_coro, args)
    ioloop.IOLoop.current().run_sync(c)

