#!/usr/bin/env python

# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.


from binascii import hexlify
import getpass
import os
from paramiko.py3compat import input

import paramiko

try:
    import interactive
except ImportError:
    from . import interactive


def agent_auth(transport, username):
    """
    Attempt to authenticate to the given transport using any of the private
    keys available from an SSH agent.
    """

    agent = paramiko.Agent()
    agent_keys = agent.get_keys()
    if len(agent_keys) == 0:
        return

    for key in agent_keys:
        print('Trying ssh-agent key %s' % hexlify(key.get_fingerprint()))
        try:
            transport.auth_publickey(username, key)
            print('... success!')
            return
        except paramiko.SSHException:
            print('... nope.')


def manual_auth(username, hostname, t,password):
    default_auth = 'p'
    # auth = input('Auth by (p)assword, (r)sa key, or (d)ss key? [%s] ' % default_auth)
    auth = 'p'
    if len(auth) == 0:
        auth = default_auth

    if auth == 'r':
        default_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
        path = input('RSA key [%s]: ' % default_path)
        if len(path) == 0:
            path = default_path
        try:
            key = paramiko.RSAKey.from_private_key_file(path)
        except paramiko.PasswordRequiredException:
            password = getpass.getpass('RSA key password: ')
            key = paramiko.RSAKey.from_private_key_file(path, password)
        t.auth_publickey(username, key)
    elif auth == 'd':
        default_path = os.path.join(os.environ['HOME'], '.ssh', 'id_dsa')
        path = input('DSS key [%s]: ' % default_path)
        if len(path) == 0:
            path = default_path
        try:
            key = paramiko.DSSKey.from_private_key_file(path)
        except paramiko.PasswordRequiredException:
            password = getpass.getpass('DSS key password: ')
            key = paramiko.DSSKey.from_private_key_file(path, password)
        t.auth_publickey(username, key)
    else:
        # pw = getpass.getpass('Password for %s@%s: ' % (username, hostname))
        t.auth_password(username, password)
