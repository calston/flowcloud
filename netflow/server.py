from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task
from twisted.application import service, internet 
from twisted.web.client import getPage

import binascii, time, zlib, urllib, json

from netflow import protocol

class DatagramReceiver(DatagramProtocol):
    def __init__(self, *a):
        self.flowCache = {}
        self.flowSeen = []

        self.exporter = task.LoopingCall(self.aggregateFlows)
        self.exporter.start(60.0)
        

    def datagramReceived(self, data, (host, port)):
        #print "received %r from %s:%d" % (data, host, port)
        flows = protocol.Netflow(data, host).flowlist

        for flow in flows:
            if flow['srcaddr'] in ['255.255.255.255', '0.0.0.0']:
                continue
            if flow['dstaddr'] in ['255.255.255.255', '0.0.0.0']:
                continue

            dedupeHash = binascii.crc32(repr(flow))
            if dedupeHash in self.flowSeen:
                continue 
            self.flowSeen.append(dedupeHash)

            flowHash = flow['flowhash']
            if flowHash in self.flowCache:
                self.flowCache[flowHash]['dPkts']+= flow['dPkts']
                self.flowCache[flowHash]['dOctets']+= flow['dOctets']

                if flow['first'] < self.flowCache[flowHash]['first']:
                    self.flowCache[flowHash]['first'] = flow['first']

                if flow['last'] > self.flowCache[flowHash]['last']:
                    self.flowCache[flowHash]['last'] = flow['last']
            else:
                self.flowCache[flowHash] = flow

            self.flowCache[flowHash]['lastUpdate'] = time.time()

    def exportFlows(self, flows):
        print "Exporting %s flows" % (len(flows))
        bundle = zlib.compress(json.dumps(flows, separators=(',',':')))

        return getPage(
            "http://localhost:8888/postFlows/", 
            method="POST", 
            postdata=urllib.urlencode({'flows':bundle}), 
            headers={'Content-Type':'application/x-www-form-urlencoded'}
        )
    
    def purgeFlows(self, res, purge):
        for i in purge:
            del self.flowCache[i]

    def exportError(self, error):
        print "Error exporting flows", error

    def aggregateFlows(self):
        if not self.flowCache:
            return
        export = []
        purge = []
        for hash, flow in self.flowCache.items():
            if time.time() - flow['lastUpdate'] > 60:
                # Export this flow... XXX 
                #print '%s:%s -> %s:%s | data:%s  time:%ss' % (flow['srcaddr'], flow['srcport'], flow['dstaddr'], flow['dstport'], flow['dOctets'], (flow['last']-flow['first'])/1000)
                export.append((
                    flow['router'], flow['srcaddr'], flow['dstaddr'], flow['srcport'], flow['dstport'], flow['input'], flow['output'], 
                    flow['dPkts'], flow['dOctets'], flow['last']-flow['first'], flow['lastUpdate'], flow['proto'], flow['tos']
                ))
                purge.append(hash)
    
        if export:
            self.exportFlows(export).addCallback(self.purgeFlows, purge).addErrback(self.exportError)

