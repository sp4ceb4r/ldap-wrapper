def _add_newline(fn):
    def wrapper(self, *args, **kwargs):
        self._ldif.append('\n')
        fn(self, *args, **kwargs)
    return wrapper

def _add_dn(fn):
    def wrapper(self, *args, **kwargs):
        self._ldif.append(self._format_string.format('dn', args[0]))
        fn(self, *args, **kwargs)
    return wrapper

class Writer:
    _format_string = '{0}: {1}\n'
    _encrypted_format_string = '{0}:: {1}\n'
    _CHANGETYPE = 'changetype'
    DELETE = 'delete'
    ADD = 'add'
    REPLACE = 'replace'
    MOD = 'modify'
    MOD_RDN = 'modrdn'

    def __init__(self, encrypted_fields=None):
        self._ldif = []
        fields = encrypted_fields
        if not fields:
            fields = []
        self.encryped_fields = fields

    @_add_newline
    @_add_dn
    def add_entry(self, dn, obj):
        self._ldif.append(self._format_string.format(self._CHANGETYPE,  self.ADD))
        tmp = self._ldif
        self._ldif = tmp + self._to_ldif(obj)

    @_add_newline
    @_add_dn
    def modify_entry(self, dn, obj, type=ADD):
        self._ldif.append(self._format_string.format(self._CHANGETYPE, self.MOD))
        is_first = True
        for key in obj.keys():
            self._modify_attribute(key, obj[key], type=type, is_first=is_first)
            is_first = False

    @_add_newline
    @_add_dn
    def delete_entry(self, dn):
        self._ldif.append(self._format_string.format(self._CHANGETYPE, self.DELETE))

    @_add_newline
    @_add_dn
    def modify_entry_rdn(self, dn, new_rdn, keep_old=False):
        self._ldif.append(self._format_string.format(self._CHANGETYPE, self.MOD_RDN))
        self._ldif.append(self._format_string.format('newrdn', new_rdn))
        old_rdn = 1
        if keep_old:
            old_rdn = 0
        self._ldif.append(self._format_string.format('deleteoldrdn', old_rdn))

    @_add_newline
    @_add_dn
    def delete_attribute(self, dn, attr, values=None):
        self._ldif.append(self._format_string.format(self._CHANGETYPE, self.MOD))
        self._ldif.append(self._format_string.format(self.DELETE, attr))

        if values:
            for val in values:
                self._ldif.append(self._format_string.format(attr, val))

    @_add_newline
    @_add_dn
    def modify_attribute(self, dn, attr, values=None, type=ADD):
        self._ldif.append(self._format_string.format(self._CHANGETYPE, self.MOD))
        self._modify_attribute(attr, values, type=type)

    def write(self):
        return 'version: 1\n' + ''.join(self._ldif)

    def write_to_file(self, filename):
        with open(filename, 'w+') as outfile:
            outfile.write(self.write())

    def _to_ldif(self, obj):
        ldif = []
        for attr in obj.keys():
            if isinstance(obj[attr], list):
                for val in obj[attr]:
                    ldif.append(self._format_string.format(attr, val))
            else:
                ldif.append(self._format_string.format(attr, obj[attr]))

        return ldif

    def _modify_attribute(self, attr, values, type=ADD, is_first=True):
        format_string = self._get_format_string(attr)
        if not is_first:
            self._ldif.append('-\n')
        if not values:
            values = []

        self._ldif.append(self._format_string.format(type, attr))
        for val in values:
            self._ldif.append(format_string.format(attr, val))

    def _get_format_string(self, attr):
        if attr in self.encryped_fields:
            return self._encrypted_format_string
        return self._format_string


if __name__ == '__main__':
    print 'non existant tests'
