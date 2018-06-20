# (c) 2018, Yunge Zhu <yungez@microsoft.com>
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
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import random
import shlex
import shutil
import subprocess
import sys
import tempfile
import warnings
from binascii import hexlify
from binascii import unhexlify
from binascii import Error as BinasciiError

from ansible.errors import AnsibleError, AnsibleAssertionError
from ansible import constants as C
from ansible.module_utils.six import PY3, binary_type
# Note: on py2, this zip is izip not the list based zip() builtin
from ansible.module_utils.six.moves import zip
from ansible.module_utils._text import to_bytes, to_text, to_native
from ansible.utils.path import makedirs_safe

try:
    from __main__ import display
    from azure.keyvault import KeyVaultClient, KeyVaultAuthentication, KeyVaultId
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.keyvault.models.key_vault_error import KeyVaultErrorException
except ImportError:
    from ansible.utils.display import Display
    display = Display()

def is_azure_keyvault_secret(data):
    """ Test if this is azure key vault data blob
        :arg data: a byte or text string
        :returns: True  if it's recognized. Otherwise, False.
    """
    try:
        text_data = to_text(data, encoding='utf-8')
    except (UnicodeError, TypeError):
        return False
    
    if text_data.startswith('$AZURE_KV:'):
        return True
    return False

def parse_azure_keyvault_envelope(vaulttext_envelope):
    tempdata = vaulttext_envelope.strip().split(';')

    vault_uri = tempdata[1]
    secret = tempdata[2]

    tempsecret = secret.split('/')

    return vault_uri, tempsecret[0], tempsecret[1]

def acquire_azure_keyvault_access_token():
    return ''

def get_secret(token, vaulturi, secret_name, secret_version):

    try:
        client = KeyVaultClient(KeyVaultAuthentication(token))
        secret_bundle = client.get_secret(vaulturi, secret_name, secret_version)

        if secret_bundle:
            return secret_bundle.value
    except KeyVaultErrorException as e:
        raise AnsibleError("Failed to get secret from Azure Key Vault: {0}".format(str(e)))

    return None

def get_azure_keyvault_secret(data):
    tempdata = parse_azure_keyvault_envelope(data)
    token = acquire_azure_keyvault_access_token()

    return get_secret(token, tempdata[0], tempdata[1], tempdata[2])



