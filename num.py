#!/usr/bin/env python3.1
#
# Simple numeric base printer.
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

import sys

if __name__ == '__main__':

    try:
        s = sys.argv[1].lower()
        if '0x' in s: b = 16
        elif '0o' in s: b = 8
        elif '0b' in s: b = 2
        else: b = 0
        i = int(s,b)

        print("%s: %s %s %s %s" % (s, bin(i), oct(i), i, hex(i)))
    except:
        sys.stderr.write(
            'Usage: %s <n>\n' % (sys.argv[0],)
            +'  Print <n> in bases 2, 8, 10, 16.\n'
            +'  Prefix with 0b, 0o, 0x to convert binary, octal, hex inputs.\n')
