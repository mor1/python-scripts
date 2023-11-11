#!/usr/bin/env python
#
# Copyright (C) 2012 Richard Mortier <mort@cantab.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# this script enables `unifdef/all` to be called with the correct includes and
# defines when preprocessing a source tree for code line counting. use it by
# passing, using an absolute path, to configure,

# eg., `CC=$(where cc4unifdef.py) ./configure`

# then `make` as normal. resulting ifdef-stripped files are next to their
# input, with the extension ".un" added.

import sys, os

UNIFDEF = "LC_COLLATE=C unifdefall"
GCC     = "/usr/bin/gcc"

FILES = []
INCS  = []
DEFS  = []
include = False

args = sys.argv[1:]
for a in args:
    if (a.endswith(".c") or a.endswith(".h")
            or a.endswith(".cc") or a.endswith(".cpp") or a.endswith(".hh")):

        if not include:
            FILES.append(a)
            include = False
    elif a.startswith("-I"): INCS.append(a)
    elif a.startswith("-D"): DEFS.append(a)
    elif a == "-include": include = True

for f in FILES:
    s = "%s %s %s %s >| %s.un" % (
      UNIFDEF, " ".join(INCS), " ".join(DEFS), f, f)
    print >>sys.stderr, "##", s
    os.system(s)

os.system("%s %s" % (GCC, " ".join(sys.argv[1:])))
