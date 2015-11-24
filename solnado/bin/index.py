

def solnado_cmd(subparsers):
    index_subparser = subparsers.add_parser('index')
    index_subparser.add_argument("a")
    index_subparser.set_defaults(func=main)

def main(args):
    print args
