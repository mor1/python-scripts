#!/usr/bin/env python3

# Copyright (C) 2010 Richard Mortier <mort@cantab.net>. All Rights Reserved.
#
# Licensed under the GPL v3; see LICENSE.md in the root of this distribution or
# the full text at https://opensource.org/licenses/GPL-3.0

# Simple command-line JSON pretty-printer. Deprecated for ` ... | jq .`.

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
