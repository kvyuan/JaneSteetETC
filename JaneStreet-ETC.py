########################################################################################################################
#Authors: Hao Yuan, Yuanzhe Liu
#Created on: Octobor 13, 2018
#Code organized by: Hao Yuan
#Code organized on: October 15, 2018
#Contact: hyuan95@outlook.com

########################################Jane Street Electronic Trading Challenge########################################
# encoding: utf-8
from __future__ import print_function
from socket import *
from socket import error as socket_error
import sys
import json
import time


#declare global variables for tcp connection
TEAMNAME="FOMO"
test_mode = False #Flase means the code will run in production
test_exchange_index=0
prod_exchange_hostname="production"
port = 25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + TEAMNAME if test_mode else prod_exchange_hostname
serverstatus = 1

#declare global variables for ticker price history and order id storage
valbz = []
vale = []
xlf = []
bond = []
gs = []
ms = []
wfc = []
orderid = 0

#establish TCP connection
def TCPconnect():
    global serverstatus
    s = socket(AF_INET,SOCK_STREAM)
    print ("Start connecting to the serve...")
    s.connect((exchange_hostname, port))
    print ("Server Connection Established.")
    serverstatus = 1
    return s.makefile('rw', 1)

#read information from the exchange stream
def read_from_exchange(exchange):
    return json.loads(exchange.readline())

#post information to the exchange
def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

#collect price history of securities we are interested in trading
def server_info(exchange):
    global serverstatus
    count = 0
    print ("Updating Server info...")
    while(count<1000):
        info = read_from_exchange(exchange)
        if not info:
            break
        type = info["type"]
        if(type == "close"):
            serverstatus = 0;
            print ("Server closed.")
            return
        if(type == "trade"):
            
            if(info["symbol"] == "VALBZ"):
                valbz.append(info["price"])
                
            if(info["symbol"] == "VALE"):
                vale.append(info["price"])

            if (info["symbol"] == "XLF"):
                xlf.append(info["price"])

            if (info["symbol"] == "BOND"):
                bond.append(info["price"])

            if (info["symbol"] == "GS"):
                gs.append(info["price"])

            if (info["symbol"] == "MS"):
                ms.append(info["price"])

            if (info["symbol"] == "WFC"):
                wfc.append(info["price"])

        time.sleep(0.01)
        count += 1

#define average calculation
def mean(l):
    return sum(l)//len(l)

####################################################Core Strategies#####################################################

#common stock & its ADR pair trading strategy
def ADRSignal(cs_trade_price_list, adr_trade_price_list):
    cs_mean = mean(cs_trade_price_list)
    adr_mean = mean(adr_trade_price_list)
    fair_diff = cs_mean - adr_mean
    if (fair_diff >= 2):
        return [True, adr_mean, cs_mean]

#etf arbitrage trading strategy
def etfArbitrageSignal(XLF_trade_price, bond_trade_price, GS_trade_price, MS_trade_price, WFC_trade_price):

    XLF_mean = mean(XLF_trade_price)
    bond_mean = mean(bond_trade_price)
    GS_mean = mean(GS_trade_price)
    MS_mean = mean(MS_trade_price)
    WFC_mean = mean(WFC_trade_price)

    #find long etf arbitrage opportunities
    if 10 * XLF_mean + 150 < (3 * bond_mean + 2 * GS_mean + 3 * MS_mean + 2 * WFC_mean):
        return ["long", XLF_mean, bond_mean, GS_mean, MS_mean, WFC_mean]
    #find short etf arbitrage opportunites
    if 10 * XLF_mean - 150 > (3 * bond_mean + 2 * GS_mean + 3 * MS_mean + 2 * WFC_mean):
        return ["short", XLF_mean, bond_mean, GS_mean, MS_mean, WFC_mean]

########################################################################################################################

#Use strategies here and place orders, Woooohoooo!
def action(exchange,vale, valbz, xlf, bond, gs, ms, wfc):
    # while(True):
    global serverstatus
    global orderid

    #common stock & ADR pair trading
    if(len(vale) >= 10 and len(valbz) >= 10):
        vale = vale[-10:]
        valbz = valbz[-10:]
        result = ADRSignal(valbz, vale)
        if(result != None and result[0] == True):
            print ("\n------------------------- ADR Make Action!-------------------------\n")
            orderid +=1
            write_to_exchange(exchange, {"type" : "add", "order_id": orderid, "symbol": "VALE", "dir" : "BUY",
                                         "price": result[1]+1, "size": 10})
            
            orderid +=1
            write_to_exchange(exchange, {"type" : "convert", "order_id": orderid, "symbol": "VALE", "dir" : "SELL",
                                         "size": 10})

            orderid +=1
            write_to_exchange(exchange, {"type" : "add", "order_id": orderid, "symbol": "VALBZ", "dir" : "SELL",
                                         "price": result[2]-1, "size": 10})

    #ETF arbitrage trading
    if (len(xlf) >25 and len(bond) >= 25 and len(gs) >= 25 and len(ms) >= 25 and len(wfc) >= 25):
        xlf = xlf[-25:]
        bond = bond[-25:]
        gs = gs[-25:]
        ms = ms[-25:]
        wfc = wfc[-25:]
        etf = etfArbitrageSignal(xlf, bond, gs, ms, wfc)
        if (etf != None and etf[0] == 'long'):
            print("\n------------------------- ETF Long Make Action!-------------------------\n")
            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "XLF", "dir": "BUY",
                                         "price": etf[1] + 1, "size": 100})

            orderid += 1
            write_to_exchange(exchange,
                              {"type": "convert", "order_id": orderid, "symbol": "XLF", "dir": "SELL", "size": 100})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "BOND", "dir": "SELL",
                                         "price": etf[2] - 1, "size": 30})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "GS", "dir": "SELL",
                                         "price": etf[3] - 1, "size": 20})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "MS", "dir": "SELL",
                                         "price": etf[4] - 1, "size": 30})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "WFC", "dir": "SELL",
                                         "price": etf[5] - 1, "size": 20})

        if (etf != None and etf[0] == 'short'):
            print("\n------------------------- ETF SHORT Make Action!-------------------------\n")
            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "BOND", "dir": "BUY",
                "price": etf[2] - 1, "size": 30})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "GS", "dir": "BUY",
                                         "price": etf[3] - 1, "size": 20})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "MS", "dir": "BUY",
                                          "price": etf[4] - 1, "size": 30})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "WFC", "dir": "BUY",
                                         "price": etf[5] - 1, "size": 20})

            orderid += 1
            write_to_exchange(exchange,
                               {"type": "convert", "order_id": orderid, "symbol": "XLF", "dir": "BUY", "size": 100})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "XLF", "dir": "SELL",
                                          "price": etf[1] + 1, "size": 100})

#reconnect when the server is down
def reconnect(exchange):
    global serverstatus
    print ("\nMarket Closed. Reconnecting...\n")
    while(serverstatus == 0):
        try:
            print ("Reconnect: restablishing TCP connect")
            exchange = TCPconnect()
            write_to_exchange(exchange, {"type": "hello", "team": TEAMNAME.upper()})
            hello_from_exchange = read_from_exchange(exchange)
            print ("Reconnec: message received: " "%s" % hello_from_exchange)
            if(hello_from_exchange["type"] == "hallo"):
                serverstatus = 1
                print ("----------------Handshake Success!----------------")
            else:
                serverstatus = 0
                print ("----------------Handshake Error!----------------")
        except socket_error:
             print ("\r\nReconnect: socket error,do reconnect ")
             time.sleep(0.1)

def main():
    global serverstatus
    exchange = TCPconnect()
    print("Exchange Initialize Success.")

    write_to_exchange(exchange, {"type": "hello", "team": TEAMNAME.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    while(True):
        server_info(exchange)
        if(serverstatus == 1):
            action(exchange,vale, valbz, xlf, bond, gs, ms, wfc)
        else:
            reconnect(exchange)

def initialize():
    print ("Initializing Test Mode: ")
    print ("   Test Mode: " "%s" % test_mode)
    print ("   Port: " "%s" % port)
    print ("   Hostname: " "%s" % exchange_hostname)

if __name__ == '__main__':
    initialize()
    while True:
         try:
             main()
         except socket_error:
             print ("\r\n----------------Main: socket error,do reconnect----------------")
             time.sleep(0.1)
