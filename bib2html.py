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

HEADER = ""
JOURNAL_HEADER = ""
CONFERENCE_HEADER = ""
WORKSHOP_HEADER = ""
PATENT_HEADER = ""
TECHREPORT_HEADER = ""
FOOTER = ""

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s: <options> [files...] where available <options> are:
  -h/--help           : print this message
  -s/--strings <file> : read abbreviations in from <file>
  -o/--output <file>  : output to <file>

Default output is stdout.
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
    def key(self, v): self._key = v.lower()

    @property
    def source(self): return self._source
    @source.setter
    def source(self, v): self._source = v

class Article(Record):
    def __str__(self):
        return "[ %s ARTICLE\n\t%s ]" % (self.source,
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

    def as_html(self): return ""

class InProceedings(Record):
    def __str__(self):
        return "[ %s INPROCEEDINGS\n\t%s ]" % (self.source,
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

    def as_html(self): return ""

class Patent(Record):
    def __str__(self):
        return "[ %s PATENT\n\t%s ]" % (self.source,
            "\n\t".join((
                self.values.get("title", ""), self.values.get("author", ""),
                self.values.get("number", "(unnumbered)"),
                self.values.get("doi", ""),
                self.values.get("day", ""),
                self.values.get("month", ""),
                self.values.get("year", ""),
                )))

    def as_html(self): return ""

class TechReport(Record):
    def __str__(self):
        return "[ %s TECHREPORT\n\t%s ]" % (self.source,
            "\n\t".join((
                self.values.get("title", ""), self.values.get("author", ""),
                self.values.get("number", "(unnumbered)"),
                self.values.get("institution"),
                self.values.get("month", ""), self.values.get("year", ""),
                self.values.get("url", ""),
                )))

    def as_html(self): return ""

RECORDTYPES = {
    'article': Article,
    'inproceedings': InProceedings,
    'patent': Patent,
    'techreport': TechReport,
    }
    
_complete_re = re.compile("^\}$")
_entry_re = re.compile("@(?P<entry>\w+)\{(?P<label>.+),$")
_field_re = re.compile("(?P<key>\w+)\s*=\s*(?P<value>.*)$")
def parse(args):
    records = {}
    for inp in args:
        with open(inp) as inf:
            cnt = 0
            for line in map(lambda l:l.strip(), inf.readlines()):
                cnt += 1
                try:
                    if len(line) == 0: continue

                    m = _complete_re.match(line)
                    if m:
                        label = record.label
                        if label in records:
                            raise Exception("collision! label=%s # %s" % (
                                label,record.label,))
                        records[label] = record
                        continue

                    m = _entry_re.match(line)
                    if m:
                        entry = m.group("entry").lower()
                        record = RECORDTYPES[entry]()
                        record.source = inp
                        record.label = m.group("label")
                        continue

                    m = _field_re.match(line)
                    if m:
                        record.values[record.key] = record.value
                        record.key = m.group("key")
                        record.value = m.group("value")
                    else: record.value += " "+line

                except Exception as err:
                    print("[%s:%d]: %s\n"
                          "EXC: %s" % (inp, cnt, line, err),
                        file=sys.stderr)
                    sys.exit(1)

    return records    

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
    records = parse(args).values()

    ## output as directed
    def out(s): print(s, file=output)
    def outrs(rs): list(map(lambda r:out(r.as_html()), rs))
    
    out(HEADER)
    out(JOURNAL_HEADER)
    outrs(filter(lambda r:r.source.endswith("-journal.bib"), records))
    out(CONFERENCE_HEADER)
    outrs(filter(lambda r:r.source.endswith("-conference.bib"), records))
    out(WORKSHOP_HEADER)
    outrs(filter(lambda r:r.source.endswith("-workshop.bib"), records))
    out(PATENT_HEADER)
    outrs(filter(lambda r:r.source.endswith("-patents.bib"), records))
    out(TECHREPORT_HEADER)
    outrs(filter(lambda r:r.source.endswith("-techreport.bib"), records))
    out(FOOTER)
