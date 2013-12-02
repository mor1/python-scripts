#!/usr/bin/env python
#
# Copyright (C) 2010 Richard Mortier <mort@cantab.net>.  All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA 02111-1307, USA.

import sys, os, time

def f():
    pid = os.fork()
    if pid == 0:
        l = []
        for i in range(5000):
            print "c", i
            l.append(open("/tmp/foo%d" % (i,), "w"))
        time.sleep(30)

    elif pid > 0:
        l = []
        for i in range(5000):
            print "p", i
            l.append(open("/tmp/bar%d" % (i,), "w"))

        time.sleep(30)

if __name__ == '__main__': f()
