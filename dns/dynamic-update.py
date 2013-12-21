#!/usr/bin/env python

import dns.query
import dns.resolver
import dns.reversename
import dns.update
import socket


hostname = socket.gethostname()
server_addr = 'ns.skynet.hiveary.com'
fqdn = '%s.skynet.hiveary.com.' % hostname
ttl = 7200

# Find the address of the interface facing the DNS server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((server_addr, 53))
eth_ip = sock.getsockname()[0]
sock.close()

skynet_update = dns.update.Update('skynet.hiveary.com.')
# Remove the record if it already exists to prevent duplicates, then add the new address
skynet_update.delete(fqdn, 'A')
skynet_update.add(fqdn, ttl, 'A', eth_ip)

# Add the server to the DNS load balancing for its service
# The hostname is formatted as "IDENTIFIER-SERVICE-ENVIRONMENT"
service = hostname.split('-')[1]
current_addresses = dns.resolver.query(service)
addrs = [a.address for a in current_addresses]
if eth_ip not in addrs:
  skynet_update.add(service, ttl, 'A', eth_ip)

ptr_update = dns.update.Update('37.13.in-addr.arpa.')
# Remove the record if it already exists to prevent duplicates, then add the new address
ptr_update.delete(dns.reversename.from_address(eth_ip), 'PTR')
ptr_update.add(dns.reversename.from_address(eth_ip), ttl, 'PTR', fqdn)

dns.query.tcp(skynet_update, server_addr)
dns.query.tcp(ptr_update, server_addr)
