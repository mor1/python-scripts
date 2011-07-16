#!/usr/bin/env python3.1
#
# Convert BibTeX files to json.  Makes some assumptions about the
# format of the .bib inputs, particularly that they're well-formed but
# also that the closing brace of each entry occurs by itself on a
# line.  Just run it through the Emacs bibtex-mode "reformat-buffer"
# function...
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

import re, sys, getopt, os, json, pprint

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s: <options> [files...] where available <options> are:
  -h/--help            : print this message
  -s/--strings <file>  : read abbreviations in from <file>
    """ % (err, sys.argv[0],))
    
    sys.exit(code)

_complete_re = re.compile("^\}$")
_entry_re = re.compile("@(?P<entry>\w+)\{(?P<label>.+),$")
_field_re = re.compile("(?P<key>\w+)\s*=\s*(?P<value>.*)$")
_strip_map = str.maketrans({
    '"': None,
    '{': None,
    '}': None,
    })
def parse(args, strings={}):
    records = {}
    for inp in args:
        with open(inp) as inf:
            record = {}
            key = value = None
            cnt = 0            
            for line in map(lambda l:l.strip(), inf.readlines()):
                cnt += 1
                if verbose: print("[%s:%d]: '%s'" % (inp, cnt, line))
                
                if len(line) == 0: continue

                m = _complete_re.match(line)
                if m:
                    for k in record:
                        record[k] = record[k].translate(_strip_map).rstrip(",")

                    if 'author' in record:
                        record['author'] = [
                            a.rstrip(",") for a in record['author'].split(" and ") ]

                    label = record['_label']
                    if label in records:
                        raise Exception("collision! label=%s" % (label,))
                    del record['_label']
                    records[label] = record
                    record = {}
                    continue

                m = _entry_re.match(line)
                if m:
                    entry = m.group("entry").lower()
                    record['_type'] = entry
                    record['_venue'] = os.path.basename(inp).split("-")[1].split(".")[0]
                    record['_label'] = m.group("label")
                    continue

                m = _field_re.match(line)
                if not m: record[key] += " "+line
                else: 
                    key = m.group("key").lower()
                    if key not in record: record[key] = ""

                    value = m.group("value").rstrip(",")
                    record[key] += strings.get(value, value)

    return { "count": len(records), "records": records }

_string_re = re.compile("^@string\{(?P<key>\w+)=(?P<value>.*)\}$")
def parse_strings(inp):
    strings = {}
    with open(inp) as inf:
        cnt = 0
        for line in map(lambda l:l.strip(), inf.readlines()):
            cnt += 1
            if verbose: print("[%s:%d]: '%s'" % (inp, cnt, line))
            
            m = _string_re.match(line)
            if m:
                key, value = m.group("key"), m.group("value")
                if key in strings:
                    raise Exception("collision! key=%s # %s" % (key,strings.key,))
                strings[key] = value

    return strings    

if __name__ == '__main__':
    global verbose
    verbose = False
    ## option parsing    
    pairs = [ "h/help", "o:/output=", "s:/strings=", "v/verbose", ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    output = sys.stdout
    strings = None
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-o", "--output"): output = open(a, "w+a")
            elif o in ("-s", "--strings"): strings = a
            elif o in ("-v", "--verbose"): verbose = True

            else: raise Exception("unhandled option")
    except Exception as err: die_with_usage(err, 3)

    ## parse input
    if strings: strings = parse_strings(strings)
    if len(args) == 0: die_with_usage("no input file given")
    records = parse(args, strings)
    print(json.JSONEncoder(ensure_ascii=True).encode(records))
