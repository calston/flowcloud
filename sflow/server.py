from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task
from twisted.application import service, internet 
from twisted.web.client import getPage

import binascii, time, zlib, urllib, json

#from sflow import protocol


class DatagramReceiver(DatagramProtocol):
    def __init__(self, *a):
        self.flowCache = {}
        self.flowSeen = []

    def datagramReceived(self, data, (host, port)):
        print repr(data)
