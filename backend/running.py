#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# setup logging
import paramiko
import sys,os
import socket
import traceback
import getpass
import interactive
from paramiko_auth import manual_auth, agent_auth


def ssh_connint(hostname,username,password,port=22):
    paramiko.util.log_to_file('demo.log')

    # username = ''
    # if len(sys.argv) > 1:
    #     hostname = sys.argv[1]
    #     if hostname.find('@') >= 0:
    #         username, hostname = hostname.split('@')
    # else:
    #     hostname = raw_input('Hostname: ')
    # if len(hostname) == 0:
    #     print('*** Hostname required.')
    #     sys.exit(1)
    # port = 22
    # if hostname.find(':') >= 0:
    #     hostname, portstr = hostname.split(':')
    #     port = int(portstr)

    # now connect
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
    except Exception as e:
        print('*** Connect failed: ' + str(e))
        traceback.print_exc()
        sys.exit(1)

    try:
        t = paramiko.Transport(sock)
        try:
            t.start_client()
        except paramiko.SSHException:
            print('*** SSH negotiation failed.')
            sys.exit(1)

        try:
            keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        except IOError:
            try:
                keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
            except IOError:
                print('*** Unable to open host keys file')
                keys = {}

        # check server's host key -- this is important.
        key = t.get_remote_server_key()
        if hostname not in keys:
            print('*** WARNING: Unknown host key!')
        elif key.get_name() not in keys[hostname]:
            print('*** WARNING: Unknown host key!')
        elif keys[hostname][key.get_name()] != key:
            print('*** WARNING: Host key has changed!!!')
            sys.exit(1)
        else:
            print('*** Host key OK.')

        # get username
        # if username == '':
        #     default_username = getpass.getuser()
        #     username = raw_input('Username [%s]: ' % default_username)
        #     if len(username) == 0:
        #         username = default_username

        agent_auth(t, username)
        if not t.is_authenticated():
            manual_auth(username, hostname, t,password)
        if not t.is_authenticated():
            print('*** Authentication failed. :(')
            t.close()
            sys.exit(1)

        chan = t.open_session()
        chan.get_pty()
        chan.invoke_shell()
        print('*** Here we go!\n')
        interactive.interactive_shell(chan)
        chan.close()
        t.close()

    except Exception as e:
        print('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
        sys.exit(1)

ssh_connint()