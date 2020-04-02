#!/usr/bin/env python3

# Copyright (C) 2020 Richard Mortier <mort@cantab.net>. All Rights Reserved.
#
# Licensed under the GPL v3; see LICENSE.md in the root of this distribution or
# the full text at https://opensource.org/licenses/GPL-3.0

# Computes total and all (src, dst) pairs bandwidth given a PCAP trace.
# Currently assumes a "cooked Linux" (SLL) format trace captured using `tcpdump
# -i any` from a mininet simulation.
#
# Requires `pip|pip3 install dpkt`.
#
# Useful pre-processing command lines for large PCAP files include:
#
# $ editcap -S0 -d -A"YYYY-MM-DD HH:mm:SS" -B"YYYY-MM-DD HH:mm:SS" in.pcap \
#     fragment.pcap

import sys, socket, pprint, json
import dpkt
import argparse

## dpkt.pcap.Reader iterator doesn't provide the PCAP header, only the timestamp
class R(dpkt.pcap.Reader):
    def __iter__(self):
        while 1:
            buf = self._Reader__f.read(dpkt.pcap.PktHdr.__hdr_len__)
            if not buf:
                break
            hdr = self._Reader__ph(buf)
            buf = self._Reader__f.read(hdr.caplen)
            yield (hdr.tv_sec + (hdr.tv_usec / self._divisor), hdr, buf)

## from dpkt print_pcap example
def inet_to_str(inet):
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get the bandwidth per window from a pcap file.")
    parser.add_argument('INPUT', help="Pcap file to analyse")
    parser.add_argument('-w', '--window', dest="WINDOW", default=1, help="Window size for bandwidth averaging. Measured in seconds", type=int)
    parser.add_argument('HOSTS', default=[], help="Hosts to calculate bandwith usage between", nargs='*')
    args = parser.parse_args()

    INPUT  = args.INPUT
    WINDOW = args.WINDOW ## seconds
    HOSTS  = args.HOSTS

    with open(INPUT, 'rb') as f:
        pcap = R(f)
        cnt = 0
        prevts = 0
        prevwindow = 0
        totbw  = 0
        hostbw = { i: { j: 0 for j in HOSTS } for i in HOSTS }
        for ts, hdr, buf in pcap:
            if prevts == 0:
                s = ",".join(
                    ",".join([":".join([s,d]) for d in HOSTS])
                    for s in HOSTS
                )
                print("# time,totalbw,%s" % s, sep=",", flush=True)
            cnt += 1
            if cnt % 10000 == 0:
                print(cnt, "...", end="", sep="", flush=True, file=sys.stderr)

            sll = dpkt.sll.SLL(buf) ## i happen to know the input linktype = SLL

            pkt = None
            if sll.ethtype == 0x0800: ## IPv4
                if sll.type == 3: ## sent to someone else
                    pkt = sll.ip
                elif sll.type == 4: ## sent by us, ie., emitted from switch
                    pass
                else:
                    print("[dropped %04x / %d]..." % (sll.ethtype, sll.type),
                          end="", sep="", file=sys.stderr)
            elif sll.ethtype == 0x0806: ## ARP
                print("[dropped ARP / %d bytes]..." % hdr.len,
                      end="", sep="", file=sys.stderr)
            else:
                print("[dropped %04x / %d]..." % (sll.ethtype, sll.type),
                      end="", sep="", file=sys.stderr)

            if not pkt: continue

            window = int(ts) if WINDOW == 1 else WINDOW * (int(ts) // WINDOW)
            if prevwindow == 0: prevwindow = window
            if prevwindow != window:
                hostbws = ", ".join(
                    ",".join([ str(hostbw[s][d]) for d in HOSTS ])
                     for s in HOSTS
                )
                print(prevwindow, totbw, hostbws, sep=", ", flush=True)
                totbw = 0
                hostbw = { i: { j: 0 for j in HOSTS } for i in HOSTS }
                prevwindow = window

            totbw += pkt.len
            src = inet_to_str(pkt.src)
            dst = inet_to_str(pkt.dst)
            if src in hostbw and dst in hostbw[src]:
                hostbw[src][dst] += pkt.len

            prevts = ts
