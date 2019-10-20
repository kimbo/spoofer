import argparse
import sys
import socket

import dns.message
import dns.exception

def listen_udp(port, address, timeout=3):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.bind((address, port))
    print('Listening on port {} and address {}...'.format(port, address), file=sys.stderr)
    while True:
        try:
            wire, addr = sock.recvfrom(65535)
        except socket.timeout:
            continue
        else:
            print('Got {} bytes from {}'.format(len(wire), addr))
        try:
            answer = dns.message.from_wire(wire)
        except dns.exception.DNSException as e:
            print('got DNS exception "{}": {}'.format(type(e), e), file=sys.stderr)
        else:
            print(answer)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    parser.add_argument('--addr', '--address', dest='address', default='')
    args = parser.parse_args()
    listen_udp(args.port, args.address)

if __name__ == '__main__':
    main()
