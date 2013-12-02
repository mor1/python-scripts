#!/usr/bin/env python3
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

import re, sys, getopt, os, json, pprint, time
from collections import OrderedDict

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s: <options> [files...] where available <options> are:
  -h/--help            : print this message
  -s/--strings <file>  : read abbreviations in from <file>
    """ % (err, sys.argv[0],))

    sys.exit(code)

Months = {
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
    }

_cite_re = re.compile("~\\\\cite.*$")
def munge(r):
    def _munge(s):
        def f(x):
            m = _cite_re.search(x)
            if m: x = x.split(m.group(0))[0]

            if " # ~" in x:
                m,d = x.split(" # ~")
                x = "%s %s," % (Months[m], d)

            x = x.replace("\\\\", "\\").replace("\&", "&")
            x = x.replace("\\'i", "\u0131").replace("\\'e", "\u00e9")
            x = x.replace("---", "\u2014").replace("--", "\u2013")
            x = x.replace("``", '\u201C').replace("''", '\u201D')
            x = x.replace("`", "\u2018").replace("'", "\u2019")
            return x

        if isinstance(s, type("")): s = f(s)
        elif isinstance(s, type([])): s = list(map(f, s))

        return s

    return OrderedDict(sorted([ (k,_munge(v)) for (k,v) in r.items() ]))


_complete_re = re.compile("^\}$")
_entry_re = re.compile("@(?P<entry>\w+)\{(?P<label>.+),$")
_field_re = re.compile("(?P<key>\w+)\s*=\s*(?P<value>.*)$")
_strip_map = str.maketrans({
    '"': None,
    '{': None,
    '}': None,
    })
def parse(args, strings):
    records = {}
    for inp in args:
        with open(inp) as inf:
            record = {}
            key = value = None
            cnt = 0
            for line in map(lambda l:l.strip(), inf.readlines()):
                cnt += 1
                if Verbose: print("[%s:%d]: '%s'" % (inp, cnt, line))

                if len(line) == 0: continue

                m = _complete_re.match(line)
                if m:
                    for k in record:
                        record[k] = record[k].translate(_strip_map).rstrip(",")

                    if 'author' in record:
                        record['author'] = [
                            a.rstrip(",") for a in record['author'].split(" and ") ]
                    if 'tags' in record:
                        record['tags'] = [ t.strip() for t in record['tags'].split(";") ]

                    label = record['_label']
                    if label in records:
                        raise Exception("collision! label=%s" % (label,))
                    del record['_label']

                    records[label] = munge(record)
                    record = {}
                    continue

                m = _entry_re.match(line)
                if m:
                    entry = m.group("entry").lower()
                    record['_type'] = entry
                    try:
                        venue = os.path.basename(inp).split("-")[1].split(".")[0]
                    except:
                        venue = ""
                    record['_venue'] = venue
                    record['_label'] = m.group("label")
                    continue

                m = _field_re.match(line)
                if not m: record[key] += " "+line
                else:
                    key = m.group("key").lower()
                    if key not in record: record[key] = ""

                    value = m.group("value").rstrip(",")
                    record[key] += strings.get(value, value)

    if Exc_unpublished:
        records = dict([ (k,v) for (k,v) in records.items()
                         if v['_type'] != "unpublished" ])
    records = OrderedDict(sorted(records.items()))

    return { "count": len(records), "records": records }

_string_re = re.compile("^@string\{(?P<key>\w+)=(?P<value>.*)\}$")
def parse_strings(inp):
    strings = {}
    with open(inp) as inf:
        cnt = 0
        for line in map(lambda l:l.strip(), inf.readlines()):
            cnt += 1
            if Verbose: print("[%s:%d]: '%s'" % (inp, cnt, line))

            m = _string_re.match(line)
            if m:
                key, value = m.group("key"), m.group("value")
                if key in strings:
                    raise Exception("collision! key=%s # %s" % (key,strings.key,))
                strings[key] = value

    return strings

if __name__ == '__main__':
    global Verbose, Exc_unpublished
    ## option parsing
    pairs = [ "h/help", "v/verbose","u/unpublished",
              "o:/output=", "s:/strings=", ]

    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    output = sys.stdout
    strings = None
    Verbose = False
    Exc_unpublished = True
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-o", "--output"): output = open(a, "w+a")
            elif o in ("-s", "--strings"): strings = a
            elif o in ("-v", "--verbose"): Verbose = True
            elif o in ("-u", "--unpublished"): Exc_unpublished = False

            else: raise Exception("unhandled option")
    except Exception as err: die_with_usage(err, 3)

    ## parse input
    if strings: strings = parse_strings(strings)
    else: strings = {}

    if len(args) == 0: die_with_usage("no input file given")
    records = OrderedDict(sorted(parse(args, strings).items()))
    records["tool"] = { "name": "bib2json.py",
                        "url": "https://github.com/mor1/python-scripts/blob/master/bib2json.py",
                        }
    records["date"] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    print(json.JSONEncoder(ensure_ascii=True).encode(records))
