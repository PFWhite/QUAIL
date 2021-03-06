docstr = """
Usage: quail install <root>
quail redcap generate ( <quail.conf.yaml> <project_name> <token> <url> ) [-i --initialize]
quail redcap get_meta (<project_name>) [ -q <quail.conf.yaml> ]
quail redcap get_data (<project_name>) [ -q <quail.conf.yaml> ]
quail redcap gen_meta (<project_name>) [ -q <quail.conf.yaml> ] [--batch=<batch>]
quail redcap gen_data (<project_name>) [ -q <quail.conf.yaml> ] [--batch=<batch>]
quail redcap make_import_files (<project_name>) [ -q <quail.conf.yaml> ] [--batch=<batch>]

Options:
  -h --help                                     show this message and exit
  -i --initialize                               generate the redcap project and pull metadata and data
  -b=<batch> --batch=<batch>                    the batch to do the operations on

QUAIL:

Command line args correspond to submodules in the actions module. For instance, running
$ quail redcap generate <quail.conf.yaml> <project_name> <token> <url>
calls the quail.actions.redcap.generate function. This currently is by convention.

If you are using quail for the first time to pull data from a redcap instance first
run 'quail install DIRECTORY' then the redcap generate command with the quail.conf.yaml
generated by the install and then the other commands in order in the help text.

Argument explanation:

<root>                Where the quail directory will be installed
<quail.conf.yaml>     The path to the autogenerated quail.conf.yaml in the quail root
<project_name>        A unique name for a redcap project
<token>               The api token used to access redcap data
<url>                 The api endpoint used to talk to the redcap project

"""

import os
import json
import yaml

from docopt import docopt

from quail.utils.file_manipulation_mixin import FileManipulationMixin as file_util
from quail.actions import install
from quail.actions import redcap

def find_local_config(args):
    """
    If the quail.conf.yaml path is not passed we attempt to find it. We look under
    the current directory and all its subdirectories and will use the first one we find.

    If we cannot find one, we exit and give the user
    """
    for root, dirs, files in os.walk(os.getcwd()):
        for path in files:
            if path == 'quail.conf.yaml':
                conf_path = os.path.join(root, path)
                args['<quail.conf.yaml>'] = conf_path
                print('Using quail.conf.yaml at {}'.format(conf_path))
                return args
    if not args.get('<quail.conf.yaml>'):
        exit("""
        No quail.conf.yaml found under {}. Either provide one or go to an initialized QUAIL directory.
        """.format(os.getcwd()))

def main(args):
    """
    This main function should delegate to some function in the actions
    module.

    quail <actions submodule> <submodule function> *args
    """
    if not args.get('install'):
        if not args.get('<quail.conf.yaml>'):
            args = find_local_config(args)
        qc = args.get('<quail.conf.yaml>')
        if qc:
            print('Using quail config at {}'.format(qc))

    if args.get('install'):
        install.run(args.get('<root>'))

    if args.get('redcap'):
        conf = {
            'project_name': args.get('<project_name>'),
            'quail_conf': qc,
            'batch': args.get('--batch')
        }
        if args.get('generate'):
            redcap.generate(qc,
                            name=args.get('<project_name>'),
                            token=args.get('<token>'),
                            url=args.get('<url>'),
                            init=args.get('-i'))
        elif args.get('get_meta'):
            del conf['batch']
            redcap.get_meta(**conf)
        elif args.get('get_data'):
            del conf['batch']
            redcap.get_data(**conf)
        elif args.get('gen_meta'):
            redcap.gen_meta(**conf)
        elif args.get('gen_data'):
            redcap.gen_data(**conf)
        elif args.get('make_import_files'):
            redcap.make_import_files(**conf)



def cli_run():
    """
    This is the entry point to the script when run from the command line with
    as specified in the setup.py
    """
    args = docopt(docstr)
    main(args)

if __name__ == '__main__':
    cli_run()
    exit()
