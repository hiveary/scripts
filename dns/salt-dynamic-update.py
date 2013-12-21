#!/usr/bin/{{ pillar['pkgs']['python'] }}

import dns.query
import dns.resolver
import dns.reversename
import dns.update

eth_ip = '{{ salt["network.interfaces"]()["eth0"]["inet"][0]["address"] }}'
server_addr = 'ns.skynet.hiveary.com'
fqdn = '{{ grains["host"] }}.skynet.hiveary.com.'
ttl = 7200

skynet_update = dns.update.Update('skynet.hiveary.com.')
# Remove the record if it already exists to prevent duplicates, then add the new address
skynet_update.delete(fqdn, 'A')
skynet_update.add(fqdn, ttl, 'A', eth_ip)

# Add the server to the DNS load balancing for its service
# The hostname is formatted as "IDENTIFIER-SERVICE-ENVIRONMENT"
service = '{{ grains["host"] }}'.split('-')[1]
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
