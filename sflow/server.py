import time

from twisted.internet.protocol import DatagramProtocol, ClientCreator
from twisted.internet import reactor, task, defer
from twisted.application import service, internet 
from twisted.web.client import getPage

from sflow import protocol
from sflow.protocol import flows, counters

from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
from txamqp.content import Content
import txamqp.spec


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

    def get_device(self, device):
        if not device in self.flowCache:
            self.flowCache[device] = {'uptime': 0}
        
        return self.flowCache[device]

    def get_if_cache(self, device, index):
        if not device in self.flowCache:
            self.flowCache[device] = {'uptime': 0}

        if not index in self.flowCache[device]:
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
            'src': str(header.frame.ip.src),
            'dst': str(header.frame.ip.dst),
            'sport': header.frame.ip_sport,
            'dport': header.frame.ip_dport,
            'octets': header.frame.ip.total_length
        }

class DatagramReceiver(CacheMixin, DatagramProtocol):

    def __init__(self):
        spec = txamqp.spec.load('amqp-spec-0-9-1.xml')
        self.connected = False
        d = ClientCreator(reactor, AMQClient, delegate=TwistedDelegate(), vhost='/',
                spec=spec).connectTCP('127.0.0.1', 5672)
        d.addCallback(self.amqp_connected)

        self.flowCache = {}
        self.flowSeen = []

    @defer.inlineCallbacks
    def amqp_connected(self, conn):
        self.connected = True
        self.conn = conn
        yield self.conn.authenticate('carbon', 'carbon')

    def datagramReceived(self, data, (host, port)):
        sflow = protocol.Sflow(data, host)

        for sample in sflow.samples:
            if isinstance(sample, protocol.FlowSample):
                #self.process_flow_sample(sflow, sample)
                pass

            if isinstance(sample, protocol.CounterSample):
                self.process_counter_sample(sflow, sample)

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
                
                if h in in_cache['conversations']:
                    in_cache['conversations'][h].append(self.create_flow_doc(flow, v))
                    out_cache['conversations'][h].append(self.create_flow_doc(flow, v))
                else:
                    in_cache['conversations'][h] = [self.create_flow_doc(flow, v)]
                    out_cache['conversations'][h] = [self.create_flow_doc(flow, v)]

    def publish_metric(self, chan, key, val):
        content = Content('%s %s %s' % (key, val, int(time.time())))
        #content['delivery mode'] = 2
        chan.basic_publish(exchange='graphite', content=content, routing_key='graphite')

    @defer.inlineCallbacks
    def rabbitmq_counter(self, v):
        if not self.connected:
            defer.returnValue(None)

        chan = yield self.conn.channel(1)
        yield chan.channel_open()

        self.publish_metric(chan, 'if_%s.octets.in' % v.if_index, v.if_inOctets)
        self.publish_metric(chan, 'if_%s.octets.out' % v.if_index, v.if_outOctets)

        self.publish_metric(chan, 'if_%s.packets.in' % v.if_index, v.if_inPackets)
        self.publish_metric(chan, 'if_%s.packets.out' % v.if_index, v.if_outPackets)

        yield chan.channel_close()

    def process_counter_sample(self, sflow, counter):
        for k,v in counter.counters.items():
            if isinstance(v, counters.InterfaceCounters):
                idx = v.if_index

                if_cache = self.get_if_cache(sflow.host, idx)

                inOct = v.if_inOctets# - if_cache['in']['octets']
                outOct = v.if_outOctets# - if_cache['out']['octets']

                inPac = v.if_inPackets# - if_cache['in']['packets']
                outPac = v.if_outPackets# - if_cache['out']['packets']
               
                if_cache['type'] = v.if_type
                if_cache['speed'] = v.if_speed

                if_cache['in']['octets'] = v.if_inOctets
                if_cache['in']['packets'] = v.if_inPackets 
                if_cache['in']['mcast'] = v.if_inMcast
                if_cache['in']['bcast'] = v.if_inBcast
                if_cache['in']['discard'] = v.if_inDiscard 
                if_cache['in']['errors'] = v.if_inError

                if_cache['out']['octets'] = v.if_outOctets
                if_cache['out']['packets'] = v.if_outPackets 
                if_cache['out']['mcast'] = v.if_outMcast
                if_cache['out']['bcast'] = v.if_outBcast
                if_cache['out']['discard'] = v.if_outDiscard 
                if_cache['out']['errors'] = v.if_outError

                reactor.callLater(0, self.rabbitmq_counter, v)

            elif isinstance(v, counters.HostCounters):
                device = self.get_device(sflow.host)
                
                device['hostname'] = v.hostname
                device['machine_type'] = v.machine_type
                device['os_name'] = v.os_name
                device['os_release'] = v.os_release

            print v

