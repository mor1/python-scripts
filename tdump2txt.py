#!/usr/bin/env python3
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

import sys, string, getopt, os.path

PRINTABLE   = string.punctuation + string.digits + string.ascii_letters
HEX_PREFIX  = "        0x"

def die_with_usage(err="", code=0):
    print("""ERROR: %s
Usage: %s <options> where available <options> are:
  -h/--help            : print this message
  -u/--unprintable <c> : character representing unprintable input; default '.'

Takes "tcpdump -x" output on stdin, appending ASCII translation of hexdump lines
""" % (
              err, os.path.basename(sys.argv[0])))
    sys.exit(code)

def prettify(line, unprintable="."):
    ret = ""

    def hilo(word):
        n = int(word, 16)

        hi = ""
        if len(word) == 4:
            hi = chr((n>>8) & 0xff)
            if(hi not in PRINTABLE): hi = unprintable

        lo = chr(n & 0xff)
        if(lo not in PRINTABLE): lo = unprintable

        return "%s%s" % (hi, lo)

    return ''.join(list(map(hilo, line.split())))

if __name__ == '__main__':
    try:
        ## option parsing
        pairs = [ "h/help", "u:/unprintable=", ]
        shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
        longopts = [ pair.split("/")[1] for pair in pairs ]
        try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
        except getopt.GetoptError as err: die_with_usage(err, 2)

        unprintable = "."
        try:
            for o, a in opts:
                if o in ("-h", "--help"): die_with_usage()
                elif o in ("-u", "--unprintable"): unprintable = a
                else: raise Exception("unhandled option")
        except Exception as err: die_with_usage(err, 3)

        ## main loop: capture and prettify
        while 1:
            line = sys.stdin.readline().expandtabs()

            if not line.startswith(HEX_PREFIX):
                print("%s" % line.rstrip())

            else:
                index, data = line.split(":")
                data = data.strip()
                pad = " "*(45-len(data))
                print("%s: %s%s%s" % (index, data, pad, prettify(data, unprintable)))

            sys.stdout.flush()

    except KeyboardInterrupt: pass
    finally: sys.stdout.flush()
