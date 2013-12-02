#!/usr/bin/env python3
#
# Simple command-line JSON pretty-printer.
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

import sys, json, getopt

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s: <options> <files...> where available <options> are:
  -h/--help          : print this message
  -i/--indent <n>    : set pretty-print indent (def. 2)
  -l/--line          : pretty-print individual lines

Pretty print JSON <files...> specified, or stdin if none.
    """ % (err, sys.argv[0]))
    sys.exit(code)

if __name__ == '__main__':

    ## option parsing
    pairs = [ "h/help", "l/line",
              "i:/indent=", ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    indent = 2
    per_line = False
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-i", "--indent"): indent = int(a)
            elif o in ("-l", "--line"): per_line = True
            else: raise Exception("unhandled option")
    except Exception as err: die_with_usage(err, 3)

    if len(args) == 0: args = [ sys.stdin ]
    else: args = map(lambda f: open(f), args)

    ## pretty print
    for a in args:
        if per_line:
            for line in a:
                print(json.dumps(json.loads(line), indent=indent))
        else:
            print(json.dumps(json.loads(a.read()), indent=indent))
