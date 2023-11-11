#!/usr/bin/env python3.1
#
# XXX
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

import sys, getopt, subprocess

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s: <options> where available <options> are:
  -h/--help      : print this message
  -n/--numeric   : numeric addresses only
  -p/--pid <pid> : 
    """ % (err, sys.argv[0]))
    sys.exit(code)

## helpers

if __name__ == '__main__':
    ## option parsing    
    pairs = [ "h/help",
              "p:/pid=", ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    pid = None
    numeric = False
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-n", "--numeric"): numeric = True
            elif o in ("-p", "--pid"): pid = a
            else: raise Exception("unhandled option")
    except Exception as err: die_with_usage(err, 3)

    netstat_cmd = [ "netstat", "-a", ]
    if numeric: netstat_cmd.append("-n")
    netstat_output = subprocess.check_output(netstat_cmd)
    print(list(map(lambda s:s.strip().split(), netstat_output.decode().strip().split("\n"))))

    lsof_cmd = [ "lsof", 

