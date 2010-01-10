#!/usr/bin/env python3.1
#
# Parse tcpdump hex output as text. Usage is (eg.):
#    $ tcpdump -x -s 2048 | tdump2txt.py
#
# Copyright (C) 2000 Richard Mortier <mort@cantab.net>.  All Rights
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

import sys, string

PRINTABLE   = string.punctuation + string.digits + string.ascii_letters
UNPRINTABLE = '.'
HEX_PREFIX  = "        0x"

def prettify(line):
    ret = ""

    def hilo(word):
        n = int(word, 16)

        hi = ""
        if len(word) == 4:
            hi = chr((n>>8) & 0xff)
            if(hi not in PRINTABLE): hi = UNPRINTABLE

        lo = chr(n & 0xff)
        if(lo not in PRINTABLE): lo = UNPRINTABLE

        return "%s%s" % (hi, lo)

    return ''.join(list(map(hilo, line.split())))

if __name__ == '__main__':
    try:
        while 1:
            line = sys.stdin.readline().expandtabs()
            
            if not line.startswith(HEX_PREFIX):
                print("%s" % line.rstrip())
            
            else:
                index, data = line.split(":")
                data = data.strip()
                pad = " "*(45-len(data))
                print("%s: %s%s%s" % (index, data, pad, prettify(data)))

            sys.stdout.flush()
                
    except KeyboardInterrupt: pass
    finally: sys.stdout.flush()
