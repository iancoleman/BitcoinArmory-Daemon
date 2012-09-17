from twisted.web import server
from twisted.internet import reactor
from txjsonrpc.web import jsonrpc

import decimal
import os

RPC_PORT = 7070
STANDARD_FEE = 0.0005 # BTC
        
class Wallet_Json_Rpc_Server(jsonrpc.JSONRPC):

    def __init__(self, wallet):
        self.wallet = wallet

    def jsonrpc_getnewaddress(self):
        addr = self.wallet.getNextUnusedAddress()
        return addr.getAddrStr()

    def jsonrpc_getbalance(self):
        int_balance = self.wallet.getBalance()
        decimal_balance = decimal.Decimal(int_balance) / decimal.Decimal(ONE_BTC)
        return float(decimal_balance)

    def jsonrpc_getreceivedbyaddress(self, address):
        if CLI_OPTIONS.offline:
            raise ValueError('Cannot get received amount when offline')
        # Only gets correct amount for addresses in the wallet, otherwise 0
        addr160 = addrStr_to_hash160(address)
        txs = self.wallet.getAddrTxLedger(addr160)
        balance = sum([x.getValue() for x in txs if x.getValue() > 0])
        decimal_balance = decimal.Decimal(balance) / decimal.Decimal(ONE_BTC)
        float_balance = float(decimal_balance)
        return float_balance

    def jsonrpc_sendtoaddress(self, bitcoinaddress, amount):
        if CLI_OPTIONS.offline:
            raise ValueError('Cannot create transactions when offline')
        return self.create_unsigned_transaction(bitcoinaddress, amount)


        
    # https://bitcointalk.org/index.php?topic=92496.msg1126310#msg1126310
    def create_unsigned_transaction(self, bitcoinaddress_str, amount_to_send_btc):
        # Get unspent TxOutList and select the coins
        addr160_recipient = addrStr_to_hash160(bitcoinaddress_str)
        totalSend, fee = long(amount_to_send_btc * ONE_BTC), (STANDARD_FEE * ONE_BTC)
        spendBal = self.wallet.getBalance('Spendable')
        utxoList = self.wallet.getTxOutList('Spendable')
        utxoSelect = PySelectCoins(utxoList, totalSend, fee)

        minFeeRec = calcMinSuggestedFees(utxoSelect, totalSend, fee)[1]
        if fee<minFeeRec:
            if totalSend + minFeeRec > spendBal:
                raise NotEnoughCoinsError, "You can't afford the fee!"
            utxoSelect = PySelectCoins(utxoList, totalSend, minFeeRec)
            fee = minFeeRec

        if len(utxoSelect)==0:
            raise CoinSelectError, "Somehow, coin selection failed.  This shouldn't happen"

        totalSelected = sum([u.getValue() for u in utxoSelect])
        totalChange = totalSelected - (totalSend  + fee)

        outputPairs = []
        outputPairs.append( [addr160_recipient, totalSend] )
        if totalChange > 0:
            outputPairs.append( [self.wallet.getNextUnusedAddress().getAddr160(), totalChange] )

        random.shuffle(outputPairs)
        txdp = PyTxDistProposal().createFromTxOutSelection(utxoSelect, outputPairs)

        return txdp.serializeAscii()

class Armory_Daemon():

    def __init__(self):

        use_blockchain = not CLI_OPTIONS.offline
        if(use_blockchain):
            print "Loading blockchain"
            BDM_LoadBlockchainFile()

        print "Reading wallet file"
        wallet = self.find_wallet()
        
        print "Initialising server"
        reactor.listenTCP(RPC_PORT, server.Site(Wallet_Json_Rpc_Server(wallet)))

        self.NetworkingFactory = ArmoryClientFactory( \
                                func_loseConnect=self.showOfflineMsg, \
                                func_madeConnect=self.showOnlineMsg, \
                                func_newTx=self.newTxFunc)
                                
        reactor.connectTCP('127.0.0.1', BITCOIN_PORT, self.NetworkingFactory)
        
        self.start()

    def start(self):
        print "Server started"
        reactor.run()
        
    def stop(self):
        print "Server stopped"
        reator.stop()
            
    def newTxFunc(self, pytxObj):
        # Cut down version from ArmoryQt.py
        TheBDM.addNewZeroConfTx(pytxObj.serialize(), long(RightNow()), True)
        print "New incoming TX"
        TheBDM.rescanWalletZeroConf(wallet.cppWallet)

    def showOfflineMsg(self):
        print "Offline - not tracking blockchain"

    def showOnlineMsg(self):
        print "Online - tracking blockchain"

    def find_wallet(self):
        fnames = os.listdir(os.getcwd())
        for fname in fnames:
            is_wallet = fname[-7:] == ".wallet"
            is_watchonly = fname.find("watchonly") > -1
            is_backup = fname.find("backup") > -1
            if(is_wallet and is_watchonly and not is_backup):
                wallet = PyBtcWallet().readWalletFile(fname)
                print "Using wallet file %s" % fname
                return wallet
        raise ValueError('Unable to locate a watch-only wallet in %s' % os.getcwd())
            

                
if __name__ == "__main__":
    from armoryengine import *
    rpc_server = Armory_Daemon()
