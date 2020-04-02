#!/usr/bin/env python3

# Copyright (C) 2010 Richard Mortier <mort@cantab.net>. All Rights Reserved.
#
# Licensed under the GPL v3; see LICENSE.md in the root of this distribution or
# the full text at https://opensource.org/licenses/GPL-3.0

# Simple hex raw packet dump, using SOCK_RAW (Linux) or BPF (OSX).

import sys, socket, fcntl, struct, os

def wordalign(b): return (((b) + (3)) & ~(3))

class pkts:

    def __init__(self, device):
        self.device = device
        if 'PF_PACKET' in socket.__dict__:
            self._type = 'pf_packet'
            self.socket = socket.socket(
                socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
            sa = (self.dev, 0x0000)
            self.socket.bind(sa)
            self.bufsz = 1024

        else:
            for i in range(10):
                try:
                    self.socket = open("/dev/bpf%d" % i, "rb")
                    self._type = 'bpf'
                    break

                except IOError as ioe:
                    if ioe.errno in (13, ## permission denied
                                     16, ## resource busy
                                     ): pass


##             ioc = 0x40000000 | (4<<16) | (ord('B')<<8) | 113
##             buf = struct.pack('HH', 0,0)
##             print(struct.unpack('HH', fcntl.ioctl(self.socket.fileno(), ioc, buf)))

            ioc = 0x80000000 | (32<<16) | (ord('B')<<8) | 108
            buf = struct.pack('32s', 'lo0') ##en0')
            (ifname,) = struct.unpack('32s', fcntl.ioctl(self.socket.fileno(), ioc, buf))
            print(ifname.rstrip(bytes.fromhex('00')).decode())

            ioc = 0x40000000 | (4<<16) | (ord('B')<<8) | 102
            buf = struct.pack('I', 0)
            (self.bufsz,) = struct.unpack("I", fcntl.ioctl(self.socket.fileno(), ioc, buf))

    def __iter__(self):

        if self._type == 'pf_packet':
            yield self.socket.recv(1024)

        elif self._type == 'bpf':
            buf, idx, idxp = None, 0, 0
            if not buf: buf = os.read(self.socket.fileno(), self.bufsz)

            ctr = 0
            while idx+18 < len(buf):
                (secs,usecs, caplen, datalen, hdrlen) = struct.unpack('IIIIH', buf[idx:idx+18])
                idxp = wordalign(idx+hdrlen+caplen)
                print(ctr, idx, idxp, idxp-idx, "\n\t",
                      secs,usecs, caplen, datalen, hdrlen, "\n\t  ", buf[idx:idx+18])

                if idxp >= len(buf):
                    buf = buf[idx:] + os.read(self.socket.fileno(), self.bufsz)
                    idx = 0
                    idxp = idx+hdrlen+caplen
                    print("!!!", idx, idxp)

                yield buf[idx:idxp]
                idx = idxp
                ctr += 1

            print("EEK")
            print(idx, len(buf), buf[idx:])

while 1:
    for pkt in pkts('lo0'):
        print(pkt)
        sys.stdout.flush()
