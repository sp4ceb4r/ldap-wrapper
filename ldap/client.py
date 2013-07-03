import sys
import ldap
from ldap.controls import SimplePagedResultsControl

from binder import LDAPBinder
from filter import Filter


class LDAPConstants():

    PAGE_SIZE = 1000
    LDAP_TIMEOUT = None

    SUB = ldap.SCOPE_SUBTREE
    BASE = ldap.SCOPE_BASE

## WRAPS ldap
class LDAPClient(LDAPConstants):

    def __init__(self, host, bind_dn, open_ldap=False, page_size=None):
        if page_size:
            self.PAGE_SIZE = page_size

        b = LDAPBinder(host, bind_dn, open_ldap)
        try:
            self.connection = b.bind()
        except Exception, e:
            print e
            sys.exit(1)

    def __del__(self):
        self.connection.unbind()

    def release(self):
        self.connection.unbind()

    def delete_entry(self, dn):
        return self.connection.delete_s(dn)

    def get_entry(self, dn, attributes=None):
        if not attributes:
            attributes = ['*']

        filter = Filter()
        filter.add_equal('objectClass', '*')
        results = self.search(dn, filter.build(), ldap.SCOPE_BASE, attributes)
        return results[0][1]

    def search(self, search_dn, filter, scope, attributes=None):
        if not attributes:
            attributes = ['*']
        results = self.connection.search_s(
            search_dn,
            scope,
            filter,
            attrlist=attributes
        )
        return results

    def paged_search(self, search_dn, filter, scope, results_processor, attributes=None):
        if not attributes:
            attributes = ['*']

        page_control = SimplePagedResultsControl(True, self.PAGE_SIZE, '')
        serverctrls = [page_control]

        msgid = self.connection.search_ext(
            search_dn,
            scope,
            filter,
            attrlist=attributes,
            serverctrls=serverctrls
        )

        page = 0
        records = 0
        while True:
            page += 1
            try:
                result_type, results, result_msg, serverctrls = self.connection.result3(msgid=msgid, timeout=self.LDAP_TIMEOUT)

                records += len(results)
                results_processor(results)

                pagectrls = [
                    c
                    for c in serverctrls
                    if c.controlType == SimplePagedResultsControl.controlType
                ]

                if pagectrls:
                    if pagectrls[0].cookie:
                        page_control.cookie = pagectrls[0].cookie
                        msgid = self.connection.search_ext(
                            search_dn,
                            scope,
                            filter,
                            attrlist=attributes,
                            serverctrls=[page_control]
                        )
                    else:
                        break
                else:
                    break

            except ldap.LDAPError, e:
                print e
