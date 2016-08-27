#!/usr/bin/env python
import pdb
from pprint import pprint
"""
Dashd interface
----

"""

import os
import config
import subprocess
import json
import sys
import io
import re

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

class DashDaemon():
    def __init__(self, **kwargs):
        host = kwargs.get('host', '127.0.0.1')
        user = kwargs.get('user')
        password = kwargs.get('password')
        port = kwargs.get('port')

        creds = (user, password, host, port)
        self.rpc_connection = AuthServiceProxy("http://{0}:{1}@{2}:{3}".format(*creds))

    def rpc_command(self, *params):
        # split space-delimited strings into a list
        # use actual int values and not strings
        first_param = params[0].split(' ')
        method = first_param[0]

        # separate arguments into a list and use int values if necessary
        if ( method == params[0] ):
            args = self.sanitize_rpc_args(*params[1:])
        else:
            args = self.sanitize_rpc_args(*first_param[1:])

        # getattr and getattribute are over-ridden in the AuthServiceProxy
        # implementation... :/
        return self.rpc_connection.__getattr__(method)(*args)

    def clean_var(self, obj):
        val = None
        try:
            val = int(obj) if obj.isdigit() else obj
        except AttributeError as e:
            val = obj
        return val

    def sanitize_rpc_args(self, *args):
        return [self.clean_var(arg) for arg in args]

class DashConfig():

    @classmethod
    def slurp_config_file(self, filename):
        # read dash.conf config but skip commented lines
        f = io.open(filename)
        lines = []
        for line in f:
            if re.match('^\s*#', line):
                continue
            lines.append(line)
        f.close()

        # data is dash.conf without commented lines
        data = ''.join(lines)

        return data

    @classmethod
    def get_rpc_creds(self, data):
        # get rpc info from dash.conf
        match = re.findall('rpc(user|password|port)=(\w+)', data)

        # python <= 2.6
        #d = dict((key, value) for (key, value) in match)

        # python >= 2.7
        creds = { key: value for (key, value) in match }

        # standard Dash defaults...
        default_port = 9998 if ( config.network == 'mainnet' ) else 19998

        # use default port for network if not specified in dash.conf
        if not ( 'port' in creds ):
            creds[u'port'] = default_port

        # convert to an int if taken from dash.conf
        creds[u'port'] = int(creds[u'port'])

        # return a dictionary with RPC credential key, value pairs
        return creds


class CTransaction():
    tx = {}

    def __init__(self):
        tx = {
            "bcconfirmations" : 0
        }
        return None

    def load(self, txid):
        result = rpc_command("gettransaction " + txid)

        try:
            obj = json.loads(result)
            if obj:
                self.tx = obj
                return True
            else:
                print "error loading tx"
                return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            print
            print "dashd result:", result
            print
            return False

    def get_hash(self):
        return None

    def get_confirmations(self):
        return self.tx["bcconfirmations"]
