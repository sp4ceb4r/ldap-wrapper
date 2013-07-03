from getpass import getpass
import sys
import os
import ldap


class LDAPBinder():

    def __init__(self, host, bind_dn, open_ldap=False):
        self._password = getpass('Password:')

        self.server = "ldaps://"+ host +":636/"
        if open_ldap:
            self.server = "ldap://" + host + ":389/"

        self.bind_dn = bind_dn

    def bind(self):
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        ldap.set_option(ldap.OPT_X_TLS_CACERTDIR, os.path.dirname(os.path.realpath(__file__)))

        try:
            connection = ldap.initialize(self.server)
            connection.simple_bind_s(self.bind_dn, self._password)
            return connection
        except Exception, e:
            print e
            sys.exit(1)

    def unbind(self, connection):
        connection.unbind_s()

