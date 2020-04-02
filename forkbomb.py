#!/usr/bin/env python3

# Copyright (C) 2010 Richard Mortier <mort@cantab.net>. All Rights Reserved.
#
# Licensed under the GPL v3; see LICENSE.md in the root of this distribution or
# the full text at https://opensource.org/licenses/GPL-3.0

import sys, time, os

def f():
    pid = os.fork()
    if pid == 0:
        os.execv(
            "/usr/bin/env",
            ["", "python", "-c",
             "import sys, time; print time.ctime(time.time()); time.sleep(5)"])


if __name__ == '__main__':
    for i in range(long(sys.argv[1])): f()
    time.sleep(10)
