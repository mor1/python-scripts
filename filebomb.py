#!/usr/bin/env python3

# Copyright (C) 2010 Richard Mortier <mort@cantab.net>. All Rights Reserved.
#
# Licensed under the GPL v3; see LICENSE.md in the root of this distribution or
# the full text at https://opensource.org/licenses/GPL-3.0

import sys, os, time

def f():
    pid = os.fork()
    if pid == 0:
        l = []
        for i in range(5000):
            print("c", i)
            l.append(open("/tmp/foo%d" % (i,), "w"))
        time.sleep(30)

    elif pid > 0:
        l = []
        for i in range(5000):
            print("p", i)
            l.append(open("/tmp/bar%d" % (i,), "w"))

        time.sleep(30)

if __name__ == '__main__': f()
