import struct, socket, binascii
import time


class Netflow(object):
    def __init__(self, payload, host):
        self.host = host
        self.version, self.flowcount = struct.unpack_from('!HH', payload, 0)

        self.flowlist = getattr(self, 'netflow_%s' % self.version, self.notSupported)(payload)

    def notSupported(self, *a):
        print "NetFlow version %s not supported" % self.version
        return []

    def netflow_7(self, payload):
        header = payload[:24]
        flows = payload[24:]

        (
            sys_uptime, unix_secs, unix_nsecs, flow_sequence, 
        ) = struct.unpack_from('!LLLL', header, 4)

        flowlist = []

        for i in xrange(self.flowcount):
            (
                srcaddr, dstaddr, nexthop,
                in_index, out_index, 
                dpackets, doctets, flowStart, flowLast, 
                srcPort, dstPort,
                pd, tcp_flags, proto, tos, 
                src_as, dst_as, 
                src_mask, dst_mask, 
                flags, router_sc 
            ) = struct.unpack_from('!LLLHHLLLLHHBBBBHHBBHL', flows, 0)

            flows = flows[52:]

            flowhash = [srcaddr, dstaddr, srcPort, dstPort, proto]

            flowlist.append({
                'router': self.host, 
                'seq': flow_sequence, 
                'flowhash': binascii.crc32(repr(flowhash)), 
                'srcaddr':  socket.inet_ntoa(struct.pack('!L', srcaddr)), 
                'dstaddr':  socket.inet_ntoa(struct.pack('!L', dstaddr)), 
                'srcport':  srcPort,   'dstport':  dstPort,
                'input':    in_index,  'output':   out_index,
                'dPkts':    dpackets,  'dOctets':  doctets,   
                'first':    flowStart,
                'last':     flowLast,  
                'tcp_flags':flags,     'proto':    proto,     
                'tos':      tos,
            })

        return flowlist
    
    def netflow_5(self, payload):
        header = payload[:24]
        flows = payload[24:]

        (
            sys_uptime, unix_secs, unix_nsecs, flow_sequence, 
            e_type, e_id, sample_interval 
        ) = struct.unpack_from('!LLLLBBH', header, 4)

        flowlist = []

        for i in xrange(self.flowcount):
            (
                srcaddr, dstaddr, nexthop, in_index, out_index, 
                dpackets, doctets, flowStart, flowLast, srcPort, 
                dstPort, pd, flags, proto, tos, src_as, dst_as, 
                src_mask, dst_mask, pd
            ) = struct.unpack_from('!LLLHHLLLLHHBBBBHHBBH', flows, 0)

            flows = flows[48:]

            flowhash = [srcaddr, dstaddr, srcPort, dstPort, proto]

            flowlist.append({
                'router':   self.host, 
                'seq':      flow_sequence, 
                'flowhash': binascii.crc32(repr(flowhash)), 
                'srcaddr':  socket.inet_ntoa(struct.pack('!L', srcaddr)), 
                'dstaddr':  socket.inet_ntoa(struct.pack('!L', dstaddr)), 
                'srcport':  srcPort,   'dstport':  dstPort,
                'input':    in_index,  'output':   out_index,
                'dPkts':    dpackets,  'dOctets':  doctets,
                'first':    flowStart, 
                'last':     flowLast, 
                'tcp_flags':flags,     'proto':    proto,
                'tos':      tos,       
            })
        return flowlist


    def netflow_9(self, payload):
        print "Flow 9"
        header = payload[:20]
        flows = payload[20:]
        print len(header)
        sysUpTime, uSecs, sequence, sourceId = struct.unpack_from('!LLLL', header, 4)

        # Ahh fuck it, netflow 9 is bullshit
        
        return []

