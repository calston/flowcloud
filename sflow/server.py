from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task
from twisted.application import service, internet 
from twisted.web.client import getPage

import binascii, time, zlib, urllib, json

from sflow import protocol

class DatagramReceiver(DatagramProtocol):
    def __init__(self, *a):
        self.flowCache = {}
        self.flowSeen = []

    def datagramReceived(self, data, (host, port)):
        sflow = protocol.Sflow(data, host)

        for sample in sflow.samples:
            if isinstance(sample, protocol.FlowSample):
                for flow in sample.flows.values():
                    self.process_flow_sample(sflow, flow)

            if isinstance(sample, protocol.CounterSample):
                for counter in sample.counters.values():
                    self.process_counter_sample(sflow, counter)

    def process_flow_sample(self, sflow, flow):
        print flow

    def process_counter_sample(self, sflow, counter):
        print counter
