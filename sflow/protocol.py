import struct, socket, binascii
import time
import xdrlib

from construct import *


def unpack_address(u):
    addrtype = u.unpack_uint()

    if self.addrtype == 1:
        self.address = u.unpack_fopaque(4)

    if self.addrtype == 2:
        self.address = u.unpack_fopaque(16)
    
    return self.address

class IPv4Address(object):
    def __init__(self, addr_int):
        self.na = struct.pack('!L', addr_int)
    
    def __str__(self):
        return socket.inet_ntoa(self.na)

class Sflow(object):
    def __init__(self, payload, host):
        self.host = host
        u = xdrlib.Unpacker(payload)

        self.version = u.unpack_uint()

        self.samplers = {
            1: FlowSample,
            2: CounterSample
        }

        if self.version == 5:
            self.sflow_v5(u)

    def sflow_v5(self, u):
        self.addrtype = u.unpack_uint()

        if self.addrtype == 1:
            self.address = u.unpack_fstring(4)

        if self.addrtype == 2:
            self.address = u.unpack_fstring(16)

        self.sub_agent_id = u.unpack_uint()
        self.sequence_number = u.unpack_uint()
        self.uptime = u.unpack_uint()

        self.sample_count = u.unpack_uint()

        self.decode_samples(u)

        # Sort samples by sequence number
        self.samples.sort(key=lambda x: x.sequence)

    def decode_samples(self, u):
        self.samples = []
        
        for i in range(self.sample_count):
            sample_type = u.unpack_uint()
            
            self.samples.append(self.samplers[sample_type](u))

class InterfaceCounters(object):
    def __init__(self, u):
        self.if_index = u.unpack_uint()
        self.if_type = u.unpack_uint()
        self.if_speed = u.unpack_uhyper()

        self.if_mode = u.unpack_uint()
        self.if_status = u.unpack_uint()

        self.if_inOctets = u.unpack_uhyper()
        self.if_inPackets = u.unpack_uint()
        self.if_inMcast = u.unpack_uint()
        self.if_inBcast = u.unpack_uint()
        self.if_inDiscard = u.unpack_uint()
        self.if_inError = u.unpack_uint()
        self.if_unknown = u.unpack_uint()

        self.if_outOctets = u.unpack_uhyper()
        self.if_outPackets = u.unpack_uint()
        self.if_outMcast = u.unpack_uint()
        self.if_outBcast = u.unpack_uint()
        self.if_outDiscard = u.unpack_uint()
        self.if_inError = u.unpack_uint()
 
        self.if_promisc = u.unpack_uint()

class EthernetCounters(object):
    def __init__(self, u):
        self.dot3StatsAlignmentErrors = u.unpack_uint()
        self.dot3StatsFCSErrors = u.unpack_uint()
        self.dot3StatsSingleCollisionFrames = u.unpack_uint()
        self.dot3StatsMultipleCollisionFrames = u.unpack_uint()
        self.dot3StatsSQETestErrors = u.unpack_uint()
        self.dot3StatsDeferredTransmissions = u.unpack_uint()
        self.dot3StatsLateCollisions = u.unpack_uint()
        self.dot3StatsExcessiveCollisions = u.unpack_uint()
        self.dot3StatsInternalMacTransmitErrors = u.unpack_uint()
        self.dot3StatsCarrierSenseErrors = u.unpack_uint()
        self.dot3StatsFrameTooLongs = u.unpack_uint()
        self.dot3StatsInternalMacReceiveErrors = u.unpack_uint()
        self.dot3StatsSymbolErrors = u.unpack_uint()

class VLANCounters(object):
    def __init__(self, u):
        self.vlan_id = u.unpack_uint()
        self.octets = u.unpack_uhyper()
        self.ucastPkts = u.unpack_uint()
        self.multicastPkts = u.unpack_uint()
        self.broadcastPkts = u.unpack_uint()
        self.discards = u.unpack_uint()

class TokenringCounters(object):
    def __init__(self, u):
        self.dot5StatsLineErrors = u.unpack_uint()
        self.dot5StatsBurstErrors = u.unpack_uint()
        self.dot5StatsACErrors = u.unpack_uint()
        self.dot5StatsAbortTransErrors = u.unpack_uint()
        self.dot5StatsInternalErrors = u.unpack_uint()
        self.dot5StatsLostFrameErrors = u.unpack_uint()
        self.dot5StatsReceiveCongestions = u.unpack_uint()
        self.dot5StatsFrameCopiedErrors = u.unpack_uint()
        self.dot5StatsTokenErrors = u.unpack_uint()
        self.dot5StatsSoftErrors = u.unpack_uint()
        self.dot5StatsHardErrors = u.unpack_uint()
        self.dot5StatsSignalLoss = u.unpack_uint()
        self.dot5StatsTransmitBeacons = u.unpack_uint()
        self.dot5StatsRecoverys = u.unpack_uint()
        self.dot5StatsLobeWires = u.unpack_uint()
        self.dot5StatsRemoves = u.unpack_uint()
        self.dot5StatsSingles = u.unpack_uint()
        self.dot5StatsFreqErrors = u.unpack_uint()

class VGCounters(object):
    def __init__(self, u):
        self.dot5StatsLineErrors = u.unpack_uint()
        self.dot5StatsBurstErrors = u.unpack_uint()
        self.dot5StatsACErrors = u.unpack_uint()
        self.dot5StatsAbortTransErrors = u.unpack_uint()
        self.dot5StatsInternalErrors = u.unpack_uint()
        self.dot5StatsLostFrameErrors = u.unpack_uint()
        self.dot5StatsReceiveCongestions = u.unpack_uint()
        self.dot5StatsFrameCopiedErrors = u.unpack_uint()
        self.dot5StatsTokenErrors = u.unpack_uint()
        self.dot5StatsSoftErrors = u.unpack_uint()
        self.dot5StatsHardErrors = u.unpack_uint()
        self.dot5StatsSignalLoss = u.unpack_uint()
        self.dot5StatsTransmitBeacons = u.unpack_uint()
        self.dot5StatsRecoverys = u.unpack_uint()
        self.dot5StatsLobeWires = u.unpack_uint()
        self.dot5StatsRemoves = u.unpack_uint()
        self.dot5StatsSingles = u.unpack_uint()
        self.dot5StatsFreqErrors = u.unpack_uint()

class CounterSample(object):
    def __init__(self, u):

        self.size = u.unpack_uint()
        self.sequence = u.unpack_uint()

        self.source_id = u.unpack_uint()

        self.record_count = u.unpack_uint()

        self.counters = {}

        self.decoders = {
            1: InterfaceCounters,
            2: EthernetCounters,
            3: TokenringCounters,
            4: VGCounters,
            5: VLANCounters
        }

        for i in range(self.record_count):
            counter_format = u.unpack_uint()
            counter_size = u.unpack_uint()
            self.counters[counter_format] = self.decoders[counter_format](u)

class ISO8023Header(object):
    def __init__(self, data):
        frame = Struct("Frame", 
            Bytes("destination", 6),
            Bytes("source", 6),
            Enum(UBInt16("type"),
                IPv4=0x0800,
                ARP=0x0806,
                RARP=0x8035,
                X25=0x0805,
                IPX=0x8137,
                IPv6=0x86DD,
                VLAN=0x8100
            )
        )

        ethernet = frame.parse(data[:14])
        data = data[14:]

        self.src_mac = ethernet.destination
        self.dst_mac = ethernet.source

        if ethernet.type == 'VLAN':
            d = ord(data[0])
            self.vlan = d & 0x0fff
            self.vlan_priority = d >> 13
        
        if ethernet.type == 'IPv4':
            self.decodeIPv4(data)

        #self.typelen = u.unpack_uhyper()

    def decodeIPv4(self, data):

        ip = Struct("ip_header", 
            EmbeddedBitStruct(
                Const(Nibble("version"), 4),
                Nibble("header_length"),
            ),
            BitStruct("tos",
                Bits("precedence", 3),
                Flag("minimize_delay"),
                Flag("high_throuput"),
                Flag("high_reliability"),
                Flag("minimize_cost"),
                Padding(1),
            ),
            UBInt16("total_length"),
            UBInt16("id"),
            UBInt16("flags"),
            UBInt8("ttl"),
            Enum(UBInt8("proto"),
                UDP=0x11,
                TCP=0x06
            ),
            UBInt16("checksum"),
            UBInt32("src"),
            UBInt32("dst"),
        )


        self.ip = ip.parse(data[:ip.sizeof()])

        self.ip_src = IPv4Address(self.ip.src)
        self.ip_dst = IPv4Address(self.ip.dst)

        data = data[ip.sizeof():]

        if self.ip.proto == 'TCP':
            self.tcp = Struct("tcp",
                UBInt16("sport"),
                UBInt16("dport"),
            ).parse(data)

            self.ip_sport = self.tcp.sport
            self.ip_dport = self.tcp.dport

        if self.ip.proto == 'UDP':
            self.udp = Struct("tcp",
                UBInt16("sport"),
                UBInt16("dport"),
            ).parse(data)

            self.ip_sport = self.udp.sport
            self.ip_dport = self.udp.dport

class IPv4Header(object):
    def __init__(self, u):
        pass
        
class IPv6Header(object):
    def __init__(self, u):
        pass

class IEEE80211MACHeader(object):
    def __init__(self, u):
        pass

class PPPHeader(object):
    def __init__(self, u):
        pass

class HeaderSample(object):
    def __init__(self, u):
        self.protocol = u.unpack_uint()
        self.frame_len = u.unpack_uint()

        self.payload_removed = u.unpack_uint()

        self.sample_header = u.unpack_string()

        self.samplers = {
            1: ISO8023Header
        }

        if self.samplers.get(self.protocol):
            self.frame = self.samplers[self.protocol](
                self.sample_header
            )

class EthernetSample(object):
    def __init__(self, u):
        self.length = u.unpack_uint()
        self.src_mac = u.unpack_fopaque(6)
        self.dst_mac = u.unpack_fopaque(6)

        self.type = u.unpack_uint()

class IPV4Sample(object):
    def __init__(self, u):
        self.length = u.unpack_uint()
        self.protocol = u.unpack_uint()
        self.src_ip = u.unpack_fstring(4)
        self.dst_ip = u.unpack_fstring(4)
        self.src_port = u.unpack_uint()
        self.dst_port = u.unpack_uint()
        self.tcp_flags = u.unpack_uint()
        self.tos = u.unpack_uint()

class IPV6Sample(object):
    def __init__(self, u):
        self.length = u.unpack_uint()
        self.protocol = u.unpack_uint()
        self.src_ip = u.unpack_fstring(16)
        self.dst_ip = u.unpack_fstring(16)
        self.src_port = u.unpack_uint()
        self.dst_port = u.unpack_uint()
        self.tcp_flags = u.unpack_uint()
        self.priority = u.unpack_uint()

class SwitchSample(object):
    def __init__(self, u):
        self.src_vlan = u.unpack_uint()
        self.src_priority = u.unpack_uint()
        self.dst_vlan = u.unpack_uint()
        self.dst_priority = u.unpack_uint()

class RouterSample(object):
    def __init__(self, u):
        self.next_hop = unpack_address(u) 
        self.src_mask_len = u.unpack_uint()
        self.dst_mask_len = u.unpack_uint()

class GatewaySample(object):
    def __init__(self, u):
        self.next_hop = unpack_address(u)
        self.asn = u.unpack_uint()
        self.src_as = u.unpack_uint()
        self.src_peer_as = u.unpack_uint()

        self.as_path_type = u.unpack_uint()
        self.as_path = u.unpack_array(u.unpack_uint)

        self.communities = u.unpack_array(u.unpack_uint)
        self.localpref = u.unpack_uint()

class UserSample(object):
    def __init__(self, u):
        self.src_charset = u.unpack_uint()
        self.src_user = u.unpack_string()
        self.dst_charset = u.unpack_uint()
        self.dst_user = u.unpack_string()

class URLSample(object):
    def __init__(self, u):
        self.url_direction = u.unpack_uint()
        self.url = u.unpack_string()
        self.host = u.unpack_string()

class MPLSSample(object):
    def __init__(self, u):
        self.next_hop = unpack_address(u)
        self.in_stack = u.unpack_array(u.unpack_uint)
        self.out_stack = u.unpack_array(u.unpack_uint)

class NATSample(object):
    def __init__(self, u):
        self.src_address = unpack_address(u)
        self.dst_address = unpack_address(u)

class MPLSTunnelSample(object):
    def __init__(self, u):
        self.tunnel_lsp_name = u.unpack_string()
        self.tunnel_id = u.unpack_uint()
        self.tunnel_cos = u.unpack_uint()

class MPLSVCSample(object):
    def __init__(self, u):
        self.vc_instance_name = u.unpack_string()
        self.vc_id = u.unpack_uint()
        self.vc_cos = u.unpack_uint()

class MPLSFTNSample(object):
    def __init__(self, u):
        self.mplsFTNDescr = u.unpack_string()
        self.mplsFTNMask = u.unpack_uint()

class MPLSLDPFECSample(object):
    def __init__(self, u):
        self.mplsFecAddrPrefixLength = u.unpack_uint()

class VLANTunnelSample(object):
    def __init__(self, u):
        self.stack = u.unpack_array(u.unpack_uint)

class FlowSample(object):
    def __init__(self, u):
        self.size = u.unpack_uint()

        self.sequence = u.unpack_uint()
        self.source_id = u.unpack_uint()
        self.sample_rate = u.unpack_uint()
        self.sample_pool = u.unpack_uint()
        self.dropped_packets = u.unpack_uint()

        self.if_inIndex = u.unpack_uint()
        self.if_outIndex = u.unpack_uint()

        self.record_count = u.unpack_uint()
        
        self.flows = {}

        self.decoders = {
            1: HeaderSample,
            2: EthernetSample,
            3: IPV4Sample,
            4: IPV6Sample,
            1001: SwitchSample,
            1002: RouterSample,
            1003: GatewaySample,
            1004: UserSample,
            1005: URLSample,
            1006: MPLSSample,
            1007: NATSample,
            1008: MPLSTunnelSample,
            1009: MPLSVCSample,
            1010: MPLSFTNSample,
            1011: MPLSLDPFECSample,
            1012: VLANTunnelSample
        }

        for i in range(self.record_count):
            flow_format = u.unpack_uint()
            flow_head = u.unpack_opaque()
            flow_u = xdrlib.Unpacker(flow_head)
            self.flows[flow_format] = self.decoders[flow_format](flow_u)
