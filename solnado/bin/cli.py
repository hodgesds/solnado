from pkgutil import iter_modules
import argparse
import importlib
import os
import sys

def find_subcommands(subparsers):
    for _, mod_name, is_pkg in iter_modules([os.path.dirname(__file__)]):
        if not is_pkg and mod_name not in [sys.modules, 'cli']:
            mod_fullname = 'solnado.bin.{}'.format(mod_name)
            module = importlib.import_module(mod_fullname)
            if hasattr(module, 'solnado_cmd'):
                module.solnado_cmd(subparsers)

def main():
    parser = argparse.ArgumentParser(
        prog = "solnado",
        description = "Solnado: Command line utilities for Solr",
    )
    subparsers = parser.add_subparsers()
    find_subcommands(subparsers)
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)


if __name__ == '__main__':
    main()
