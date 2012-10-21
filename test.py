################################################################################
#
# Copyright (C) 2012, Ian Coleman
# Distributed under the GNU Affero General Public License (AGPL v3)
# See http://www.gnu.org/licenses/agpl.html
#
################################################################################

# Tests for armory-daemon.py
# Depends on jsonrpc - https://github.com/jgarzik/python-bitcoinrpc
# Ensure armory-daemon is running before commencing tests

import decimal
import json
from jsonrpc import ServiceProxy


class UniversalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

access = ServiceProxy("http://127.0.0.1:7070")

# TODO use asserts on this, for now manual inspection will do
newaddress = access.getnewaddress()
print "getnewaddress: %s" % newaddress
print "getbalance: %f" % access.getbalance()
print "getreceivedbyaddress: %f" % access.getreceivedbyaddress(newaddress)
print "sendtoaddress: %s" % access.sendtoaddress(newaddress, 0.1)
print "listtransactions: %s" % json.dumps(access.listtransactions(), sort_keys=True, indent=4, cls=UniversalEncoder)
print "\n\nlisttransactions: %s" % json.dumps(access.listtransactions(1), sort_keys=True, indent=4, cls=UniversalEncoder)
print "\n\nlisttransactions: %s" % json.dumps(access.listtransactions(1, 1), sort_keys=True, indent=4, cls=UniversalEncoder)
