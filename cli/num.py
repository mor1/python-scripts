#!/usr/bin/env python3

# Copyright (C) 2000 Richard Mortier <mort@cantab.net>. All Rights Reserved.
#
# Licensed under the GPL v3; see LICENSE.md in the root of this distribution or
# the full text at https://opensource.org/licenses/GPL-3.0

# Simple numeric base printer.

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
