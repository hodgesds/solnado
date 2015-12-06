from __future__ import print_function
from functools import partial
from tornado import gen
from tornado import ioloop
from solnado.client import SolrClient
import os

def solnado_cmd(subparsers):
    core_subparser = subparsers.add_parser('core')
    sub = core_subparser.add_subparsers()
    add_create_subparser(sub)
    add_delete_subparser(sub)
    add_status_subparser(sub)

def add_create_subparser(subparsers):
    create_subparser = subparsers.add_parser('create')
    create_subparser.set_defaults(func=create_core)
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
        'name',
        help = 'Core name'
    )
    create_subparser.add_argument(
        '-c','--config-file',
        dest    = 'conf_file',
        default = '',
        help    = 'config file to use',
    )
    create_subparser.add_argument(
        '-i', '--instance-dir',
        dest    = 'instance_dir',
        default = None,
        help    = 'Shard names',
    )

@gen.coroutine
def create_coro(args):
    c = SolrClient(host=args.host)
    collection_kwargs = {}

    p = partial(
        c.core_create,
        args.name,
        **{
            'config':            args.conf_file,
            'instance_dir':      args.instance_dir,
        }
    )
    s = yield gen.Task(p)
    print(s.body)

def create_core(args):
    c = partial(create_coro, args)
    ioloop.IOLoop.current().run_sync(c)

def add_delete_subparser(subparsers):
    delete_subparser = subparsers.add_parser('delete')
    delete_subparser.set_defaults(func=delete_core)
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
        help = 'Core name'
    )

@gen.coroutine
def delete_coro(args):
    c = SolrClient(host=args.host)
    collection_kwargs = {}

    p = partial(
        c.core_unload,
        args.name,
    )
    s = yield gen.Task(p)
    print(s.body)

def delete_core(args):
    c = partial(delete_coro, args)
    ioloop.IOLoop.current().run_sync(c)

def add_status_subparser(subparsers):
    status_subparser = subparsers.add_parser('status')
    status_subparser.set_defaults(func=core_status)
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
    status_subparser.add_argument(
        'name',
        help = 'Core name'
    )

@gen.coroutine
def status_coro(args):
    c = SolrClient(host=args.host)
    collection_kwargs = {}

    p = partial(
        c.core_status,
        **{'core': args.name}
    )
    s = yield gen.Task(p)
    print(s.body)

def core_status(args):
    c = partial(status_coro, args)
    ioloop.IOLoop.current().run_sync(c)
