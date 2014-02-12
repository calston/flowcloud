from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task
from twisted.application import service, internet 
from twisted.web.client import getPage

import binascii, time, zlib, urllib, json, socket

from sflow import protocol

class DatagramReceiver(DatagramProtocol):
    def __init__(self, *a):
        self.flowCache = {}
        self.flowSeen = []

    def datagramReceived(self, data, (host, port)):
        sflow = protocol.Sflow(data, host)

        print sflow.uptime

        for sample in sflow.samples:
            if isinstance(sample, protocol.FlowSample):
                self.process_flow_sample(sflow, sample)

            if isinstance(sample, protocol.CounterSample):
                self.process_counter_sample(sflow, sample)

    def process_flow_sample(self, sflow, flow):
        for k,v in flow.flows.items():
            if isinstance(v, protocol.HeaderSample):
                print "%s:%s -> %s:%s" % (v.frame.ip_src, v.frame.ip_sport, v.frame.ip_dst, v.frame.ip_dport)

    def process_counter_sample(self, sflow, counter):
        print counter
