from construct import *
from construct import adapters

from sflow.protocol import utils


class IPv4Header(object):
    def __init__(self, data):
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

        self.ip.src = utils.IPv4Address(self.ip.src)
        self.ip.dst = utils.IPv4Address(self.ip.dst)

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

        try:
            ethernet = frame.parse(data[:14])
        except adapters.MappingError:
            print "Broken ethernet header"
            self.frame = None
            print repr(data)
            return
        data = data[14:]

        self.src_mac = ethernet.destination
        self.dst_mac = ethernet.source

        if ethernet.type == 'VLAN':
            d = ord(data[0])
            self.vlan = d & 0x0fff
            self.vlan_priority = d >> 13
        
        elif ethernet.type == 'IPv4':
            ipv4 = IPv4Header(data)
            self.ip = ipv4.ip
            self.ip_sport = ipv4.ip_sport
            self.ip_dport = ipv4.ip_dport
        else:
            print ethernet.type, repr(data)

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
            1: ISO8023Header,
            7: PPPHeader,
            11: IPv4Header,
            12: IPv6Header
        }

        if self.samplers.get(self.protocol):
            self.frame = self.samplers[self.protocol](
                self.sample_header
            )
        else:
            print "Unknown protocol:", self.protocol
            self.frame = None

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
        self.next_hop = utils.unpack_address(u) 
        self.src_mask_len = u.unpack_uint()
        self.dst_mask_len = u.unpack_uint()

class GatewaySample(object):
    def __init__(self, u):
        self.next_hop = utils.unpack_address(u)
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
        self.next_hop = utils.unpack_address(u)
        self.in_stack = u.unpack_array(u.unpack_uint)
        self.out_stack = u.unpack_array(u.unpack_uint)

class NATSample(object):
    def __init__(self, u):
        self.src_address = utils.unpack_address(u)
        self.dst_address = utils.unpack_address(u)

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

def getDecoder(format):
    decoders = {
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
    return decoders.get(format, None)


