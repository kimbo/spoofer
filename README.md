# dns-spoofer

Send spoofed DNS queries over UDP.

# Installation

```
pip install git+https://github.com/kimbo/dns-spoofer.git
```

That will install two scripts

- `dns-spoof` - send DNS queries with a different source port and source IP address than your own.
- `dns-listen` - listen for and print UDP packets (i.e. DNS queries) on a port and address

# Quick example

This will be a little bit cooler if you have access to two different computers on the same network, 
but it'll work just the same on just one.

### Step #1: 
Open up a terminal and run:
```
$ dns-listen 53535
Listening on port 53535 and address ...
```
You can replace 53535 with whatever port number you want (I'd recommend one bigger than 1024).

Note that the address is blank (meaning we're listening on all addresses).

If you have two computers, take note of the first computer's IP address (look into `ip addr`, or `ifconfig` if you're on a Mac)

### Step #2
If you have two computers, you'll need the IP address from your first machine here:
```
$ dns-spoof example.com 1.1.1.1 --sport 53535 --src-addr <IP-address-here>
```
Otherwise, if you're doing this on one computer, run:
```
$ dns-spoof example.com 1.1.1.1 --sport 53535
```
Your output after running `dns-spoof` should look something like this:
```
(query) 192.168.0.25#53535 --> 1.1.1.1#53, "example.com" type "A"

### QUERY TIME: 0.00028133392333984375
```

Soon after running `dns-spoof`, look at the terminal you were running `dns-listen` on. 
It should have printed out something like this:
```
Got 45 bytes from ('1.1.1.1', 53)
id 62725
opcode QUERY
rcode NOERROR
flags QR RD RA
;QUESTION
example.com. IN A
;ANSWER
example.com. 3574 IN A 93.184.216.34
;AUTHORITY
;ADDITIONAL
```

Congratulations! You just sent a spoofed DNS query :smile:

# Usage for dns-spoof
```
$ dns-spoof -h
usage: dns-spoof [-h] [--dport DST_PORT] [--src-addr SRC_ADDR]
                 [--sport SRC_PORT] [-t RDTYPE] [-n NUM_QUERIES]
                 qname dst_addr

positional arguments:
  qname
  dst_addr              The address to send the DNS query to

optional arguments:
  -h, --help            show this help message and exit
  --dport DST_PORT, --destintaion-port DST_PORT
  --src-addr SRC_ADDR, --source-address SRC_ADDR
  --sport SRC_PORT, --source-port SRC_PORT
  -t RDTYPE, --rdtype RDTYPE
  -n NUM_QUERIES, --num-queries NUM_QUERIES
```

# Usage for dns-listen
```
$ dns-listen -h
usage: dns-listen [-h] [--addr ADDRESS] port

positional arguments:
  port

optional arguments:
  -h, --help            show this help message and exit
  --addr ADDRESS, --address ADDRESS
```

# Disclaimers

- I've only tested this from behind a NAT
- Only works with UDP and IPv4
- I'm not responsible for what you do with this.

# License

see [LICENSE](./LICENSE)
