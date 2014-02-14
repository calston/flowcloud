from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task
from twisted.application import service, internet 
from twisted.web.client import getPage

import binascii, time, zlib, urllib, json, socket, struct

from sflow import protocol
from sflow.protocol import flows, counters

def bitLength(c):
    if c <= 1:
        return 1

    for i in range(64):
        if c <= (2**i):
            return i

class CacheMixin(object):
    def __init__(self, *a):
        self.flowCache = {}
        self.flowSeen = []

    def get_if_cache(self, device, index):
        if not device in self.flowCache:
            self.flowCache[device] = {'uptime': 0}

        if not index in self.flowCache:
            self.flowCache[device][index] = {
                'type': 0,
                'speed': 0,
                'in':{
                    'octets': 0,
                    'packets': 0,
                    'mcast': 0,
                    'bcast': 0,
                    'discard': 0,
                    'errors': 0,
                    'conversations': {}
                },
                'out': {
                    'octets': 0,
                    'packets': 0,
                    'mcast': 0,
                    'bcast': 0,
                    'discard': 0,
                    'errors': 0,
                    'conversations': {}
                }

            }

        return self.flowCache[device][index]

    def create_flow_doc(self, flow, header):
        return {
            'sr': flow.sample_rate,
            'sp': flow.sample_pool,
            'sd': flow.dropped_packets,
            'src': header.frame.ip.src,
            'dst': header.frame.ip.dst,
            'sport': header.frame.ip_sport,
            'dport': header.frame.ip_dport,
            'octets': header.frame.ip.total_length
        }

class DatagramReceiver(CacheMixin, DatagramProtocol):

    def datagramReceived(self, data, (host, port)):
        sflow = protocol.Sflow(data, host)

        for sample in sflow.samples:
            if isinstance(sample, protocol.FlowSample):
                self.process_flow_sample(sflow, sample)

            if isinstance(sample, protocol.CounterSample):
                self.process_counter_sample(sflow, sample)

        print self.flowCache

    def process_flow_sample(self, sflow, flow):
        for k,v in flow.flows.items():
            if isinstance(v, flows.HeaderSample) and v.frame:
                if_in = flow.if_inIndex
                if_out = flow.if_outIndex

                in_cache = self.get_if_cache(sflow.host, if_in)['in']
                out_cache = self.get_if_cache(sflow.host, if_out)['out']

                src = v.frame.ip.src.addr_int
                dst = v.frame.ip.dst.addr_int

                h = src << bitLength(src)
                h = (h | dst) << bitLength(dst)
                h = (h | v.frame.ip_sport) << bitLength(v.frame.ip_sport)
                h = (h | v.frame.ip_dport)

                in_cache['conversations'][h] = self.create_flow_doc(flow, v)
                out_cache['conversations'][h] = self.create_flow_doc(flow, v)

    def process_counter_sample(self, sflow, counter):
        print counter


