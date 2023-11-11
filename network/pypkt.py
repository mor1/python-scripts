#!/usr/bin/env python3.1
#
#
#
# Copyright (C) 2010 Richard Mortier <mort@cantab.net>.  All Rights
# Reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
# USA.

import sys, socket

class socket(object):
    def __init__(self):
        if PF_PACKET in socket.__dict__:
            self._sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

dev = 'eth0'

s = 
sockaddr = (dev, 0x0000)
s.bind(sockaddr)
x = s.getsockname()
print x

while 1:
    y = s.recv(1024)
    print `y`
    sys.stdout.flush()
