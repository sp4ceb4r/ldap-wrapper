import sys
from argparse import ArgumentParser as Parser

from ldap.client import LDAPClient

PAGE_SIZE = 1000
BIND_DN = 
OPEN_DN = 

class Handler():

    def __init__(self, args=None):
        parser = Parser(description='Tell me what to do')
        parser.add_argument('host')
        parser.add_argument('-o', '--open_ldap', action='store_true')
        parser.add_argument('-b', '--bind_dn')
        parser.add_argument('-s', '--page_size', type=int)

        if args:
            for arg in args:
                parser.add_argument(*arg[0], **arg[1])

        self.parser = parser

    def handle(self):
        if len(sys.argv) > 1:
            args = vars(self.parser.parse_args())
        else:
            sys.argv.append('-h')
            self.parser.parse_args()

        if not args['bind_dn']:
            args['bind_dn'] = BIND_DN
            if args['open_ldap']:
                args['bind_dn'] = OPEN_DN

        if not args['page_size']:
            args['page_size'] = PAGE_SIZE

        client_args = self._split(args)
        return LDAPClient(**client_args), args

    def _split(self, args):
        client_args = {}
        client_args['host'] = args['host']
        del args['host']
        client_args['open_ldap'] = args['open_ldap']
        del args['open_ldap']
        client_args['page_size'] = args['page_size']
        del args['page_size']
        client_args['bind_dn'] = args['bind_dn']
        del args['bind_dn']

        return client_args

if __name__ == '__main__':
    args = [(('-a', '--about'), {'help':'this is a help message'})]
    args2 = [(('positional',), {})]

    handler = Handler(args=args)
    client = handler.handle()
    client.release()

    handler2 = Handler(args=args2)
