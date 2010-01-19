#!/usr/bin/env python3.1
#
# Convert .bib files to .html.  Edit .as_html() methods of classes
# derived from Record to change formatting.
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

import re, sys, getopt

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s: <options> where available <options> are:
  -h/--help          : print this message
  -s/--strings <file>: read abbreviations in from <file>

    """ % (err, sys.argv[0]))
    sys.exit(code)

class Record:
    def __init__(self):
        self.values = {}
        self._label = ""

    def __repr__(self): return str(self)

    @property
    def label(self): return self._label
    @label.setter
    def label(self, v): self._label = v

    @property
    def value(self):
        try: return self._value
        except: return ""
    @value.setter
    def value(self, v): self._value = v

    @property
    def key(self):
        try: return self._key
        except: return ""
    @key.setter
    def key(self, v): self._key = v

class Article(Record):
    def __str__(self):
        return "[ ARTICLE\n\t%s]" % (
            "\n\t".join((
                self.values.get("title",""), self.values.get("author",""),
                self.values.get("journal",""),
                self.values.get("volume",""),self.values.get("number",""),
                self.values.get("pages",""),
                self.values.get("month",""), self.values.get("year",""),
                self.values.get("address",""),
                self.values.get("publisher",""),
                self.values.get("doi",""),
                self.values.get("note",""),
                )))

class InProceedings(Record):
    def __str__(self):
        return "[ INPROCEEDINGS\n\t%s]" % (
            "\n\t".join((
                self.values.get("title",""), self.values.get("author",""),
                self.values.get("booktitle",""),
                self.values.get("pages",""),
                self.values.get("month",""), self.values.get("year",""),
                self.values.get("address",""),
                self.values.get("publisher",""),
                self.values.get("doi",""),
                self.values.get("url",""),
                self.values.get("note",""),
                )))

RECORDTYPES = {
    'article': Article,
    'inproceedings': InProceedings,
    }
    
_entry_re = re.compile("@(?P<entry>\w+)\{(?P<label>.+),$")
_field_re = re.compile("(?P<key>\w+)\s*=\s*(?P<value>.*)$")

Records = {}
if __name__ == '__main__':

    ## option parsing    
    pairs = [ "h/help", "o:/output=", "s:/strings=", ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    output = sys.stdout
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-o", "--output"): output = open(a, "w+a")
            else: raise Exception("unhandled option")
    except Exception as err: die_with_usage(err, 3)

    ## parse input
    if len(args) == 0: die_with_usage("no input file given")

    for inp in args:
        with open(inp) as inf:
            for line in map(lambda l:l.strip(), inf.readlines()):
                try:
                    if len(line) == 0: continue
                    elif line == '}':
                        label = record.label
                        if label in Records:
                            raise Exception("collision! label=%s # %s" % (label,record.label,))
                        Records[label] = record
                    
                    else:
                        m = _entry_re.match(line)
                        if m:
                            entry = m.group("entry").lower()
                            record = RECORDTYPES[entry]()
                            record.label = m.group("label")
                            continue

                        m = _field_re.match(line)
                        if m:
                            record.values[record.key] = record.value
                            record.key = m.group("key")
                            record.value = m.group("value")
                        else: record.value += " "+line

                except Exception as err:
                    print(line)
                    print(err)
                    sys.exit(1)

    print(Records, file=output)
