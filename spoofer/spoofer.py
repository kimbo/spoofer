import array
import random
import select
import socket
import struct
import sys
import time
from argparse import ArgumentParser

import dns.message

from .utils import free_port, get_my_ip_address

# https://github.com/secdev/scapy/blob/master/scapy/utils.py#L303
if struct.pack("H", 1) == b"\x00\x01":  # big endian
    def checksum(pkt):
        if len(pkt) % 2 == 1:
            pkt += b"\0"
        s = sum(array.array("H", pkt))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        s = ~s
        return s & 0xffff
else:
    def checksum(pkt):
        if len(pkt) % 2 == 1:
            pkt += b"\0"
        s = sum(array.array("H", pkt))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        s = ~s
        return (((s >> 8) & 0xff) | s << 8) & 0xffff


class Packet(object):
    def __init__(self, *args, **kwargs):
        pass

    def __bytes__(self):
        return self.to_wire()

    def __add__(self, other):
        return self.__bytes__() + bytes(other)

    def to_wire(self):
        pass

class Ip(Packet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = 4  # 4 bits
        self.ihl = 5  # header length in 32 bit words; 4 bits
        self._version_ihl = 0b01000101  # version + ihl = 8 bits
        self.type_of_service = 0  # 8 bits
        self.total_length = 20  # 16 bits
        self.identification = random.randint(0, 65535)  # 16 bits
        self.flags = 0  # 4 bits
        self.fragment_offset = 0  # 12 bits
        self._flags_offset = 0  # flags + fragment_offset = 16 bits
        self.ttl = 64  # 8 bits
        self.protocol = kwargs.get('protocol')  # 8 bits
        self.header_checksum = 0  # 16 bits
        self.source_address = socket.inet_pton(socket.AF_INET, kwargs.get('src'))  # 32 bits
        self.destination_address = socket.inet_pton(socket.AF_INET, kwargs.get('dest'))  # 32 bits
        self.options = None  # varying length

        self._checksum_packed_header = self.to_wire()
        self.header_checksum = checksum(self._checksum_packed_header)

    def to_wire(self):
        return struct.pack(">BBHHHBBH4s4s",
                           self._version_ihl, self.type_of_service, self.total_length,
                           self.identification, self._flags_offset, self.ttl,
                           self.protocol, self.header_checksum, self.source_address,
                           self.destination_address)

class Udp(Packet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.src_port = kwargs.get('src_port')  # 16 bits
        self.dest_port = kwargs.get('dest_port')  # 16 bits
        self.payload = kwargs.get('payload')
        self.length = 8 + len(self.payload)  # 16 bits
        self.checksum = 0  # 16 bits

        self.src_addr = socket.inet_pton(socket.AF_INET, kwargs.get('src_addr'))
        self.dest_addr = socket.inet_pton(socket.AF_INET, kwargs.get('dest_addr'))

        self.pub_addr = socket.inet_pton(socket.AF_INET, '75.169.193.123')
        self._pseudo_header = struct.pack(">4s4sBBH",
                                          self.pub_addr, self.dest_addr, 0, socket.IPPROTO_UDP, self.length)

        self.checksum = 0
        # self.checksum = checksum(self._pseudo_header)

    def to_wire(self):
        return struct.pack(">HHHH", self.src_port, self.dest_port, self.length, self.checksum)

def dns_query_udp(src_addr, dst_addr, src_port, dst_port, qname, rdtype, timeout=3):
    query = dns.message.make_query(qname, rdtype=rdtype)
    wire = query.to_wire()
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    sock.settimeout(timeout)
    ip = Ip(src=src_addr, dest=dst_addr, protocol=socket.IPPROTO_UDP)
    udp = Udp(src_port=src_port, dest_port=dst_port, src_addr=src_addr, dest_addr=dst_addr,
              payload=wire)
    return sock.sendto(ip + udp + wire, (dst_addr, dst_port))

def main():
    parser = ArgumentParser()
    parser.add_argument('qname', type=str)
    parser.add_argument('dst_addr', help='The address to send the DNS query to')
    parser.add_argument('--dport', '--destintaion-port', dest='dst_port', type=int, default=53)
    parser.add_argument('--src-addr', '--source-address', dest='src_addr', type=str)
    parser.add_argument('--sport', '--source-port', dest='src_port', type=str)
    parser.add_argument('-t', '--rdtype', type=str, default='A')
    parser.add_argument('-n', '--num-queries', type=int, default=1)

    args = parser.parse_args()
    num_queries = args.num_queries
    del args.num_queries
    if args.src_port is None:
        args.src_port = free_port()
    else:
        args.src_port = int(args.src_port)

    my_ip = get_my_ip_address()
    if args.src_addr is None:
        args.src_addr = my_ip

    start_time = time.time()
    for _ in range(num_queries):
        dns_query_udp(args.src_addr, args.dst_addr, args.src_port, args.dst_port, args.qname, args.rdtype)
        print('(query) {src_addr}#{src_port} --> {dst_addr}#{dst_port}, "{qname}" type "{rdtype}"'.format(**vars(args)), file=sys.stderr)
    end_time = time.time()
    print(file=sys.stderr)
    query_time = end_time - start_time
    print('### QUERY TIME: {}'.format(query_time), file=sys.stderr)
    #qps = num_queries / (end_time - start_time)
    #print('### QPS: {}'.format(qps), file=sys.stderr)

if __name__ == '__main__':
    main()
