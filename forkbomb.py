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
