# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import yaml

from ansible.module_utils.six import text_type
from ansible.module_utils._text import to_bytes, to_text
from ansible.parsing.azurekeyvault import is_azure_keyvault_secret, get_if_azure_keyvault_secret, get_secret
from ansible.parsing.yaml.objects import AnsibleBaseYAMLObject

class AzureKeyVaultUnicode(yaml.YAMLObject, AnsibleBaseYAMLObject):
    __UNSAFE__ = True
    __ENCRYPTED__ = True
    yaml_tag = u'!azurekeyvault'


    def __init__(self, envelope):
        '''A AnsibleUnicode with a Vault attribute that can decrypt it.

        ciphertext is a byte string (str on PY2, bytestring on PY3).

        The .data attribute is a property that returns the decrypted plaintext
        of the ciphertext as a PY2 unicode or PY3 string object.
        '''
        super(AzureKeyVaultUnicode, self).__init__()

        # after construction, calling code has to set the .vault attribute to a vaultlib object
        tempdata = envelope.strip().split(';')
        vault_uri = tempdata[1]
        secret = tempdata[2]
        tempsecret = secret.split('/')
        
        self.envelope = envelope
        self.vault_uri = tempdata[1]
        self.secret_name = tempsecret[0]
        self.secret_version = tempsecret[1] if len(tempsecret) >1 else ''

    @property
    def data(self):
        return get_secret(self.vault_uri, self.secret_name, self.secret_version)

    @data.setter
    def data(self, value):
        self.envelope = value

    def __repr__(self):
        return repr(self.data)

    def __eq__(self, other):
        return self.envelope == other

    def __hash__(self):
        return id(self)

    def __ne__(self, other):
        return self.envelope != other

    def __str__(self):
        return str(self.data)

    def __unicode__(self):
        return to_text(self.data, errors='surrogate_or_strict')

    def encode(self, encoding=None, errors=None):
        return self.data.encode(encoding, errors)

