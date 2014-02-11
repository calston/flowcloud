import struct, socket, binascii
import time
import xdrlib


def unpack_address(u):
    addrtype = u.unpack_uint()

    if self.addrtype == 1:
        self.address = u.unpack_fstring(4)

    if self.addrtype == 2:
        self.address = u.unpack_fstring(16)
    
    return self.address

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

        self.interface_counters = []

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
            self.interface_counters.append(self.decoders[counter_format](u))

class HeaderSample(object):
    def __init__(self, u):

        self.protocol = u.unpack_uint()
        self.frame_len = u.unpack_uint()

        self.payload_removed = u.unpack_uint()

        self.sample_header = u.unpack_string()

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
        
        self.flows = []

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
            counter_format = u.unpack_uint()
            counter_size = u.unpack_uint()
            self.flows.append(self.decoders[counter_format](u))

