#!/usr/bin/env python3.1
#
# Convert .bib files to .html.  Edit .as_html() methods of classes
# derived from Record to change formatting.  Makes some assumptions
# about the format of the .bib inputs, particularly that they're
# well-formed but also that the closing brace of each entry occurs by
# itself on a line.  Just run it through the Emacs bibtex-mode
# "reformat-buffer" function...
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

import re, sys, getopt, os

CWD = os.path.dirname(__file__)
HEADER = os.path.join(CWD, "bib2html", "header.html")
FOOTER = os.path.join(CWD, "bib2html", "footer.html")
H_JOURNALS = os.path.join(CWD, "bib2html", "h_journals.html")
H_CONFERENCES = os.path.join(CWD, "bib2html", "h_conferences.html")
H_WORKSHOPS = os.path.join(CWD, "bib2html", "h_workshops.html")
H_PATENTS = os.path.join(CWD, "bib2html", "h_patents.html")
H_TECHREPORTS = os.path.join(CWD, "bib2html", "h_techreports.html")

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s: <options> [files...] where available <options> are:
  -h/--help            : print this message
  -o/--output <file>   : output to <file>
  -s/--strings <file>  : read abbreviations in from <file>

  --header <file>      : set header template to <file>\n\t[def. %s]
  --footer <file>      : set footer template to <file>\n\t[def. %s]
  --journals <file>    : set journals header template to <file>\n\t[def. %s]
  --conferences <file> : set conferences header template to <file>\n\t[def. %s]
  --workshops <file>   : set workshops header template to <file>\n\t[def. %s]
  --patents <file>     : set patents header template to <file>\n\t[def. %s]
  --techreports <file> : set header template to <file>\n\t[def. %s]

Default output is stdout.  
    """ % (err, sys.argv[0],
           HEADER, FOOTER, H_JOURNALS, H_CONFERENCES, H_WORKSHOPS, H_PATENTS, H_TECHREPORTS))
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

    def as_html(self):
        if 'number' not in self.values: self.values['number'] = ""
        else:
            self.values["number"] = "(%s)" % (self.values["number"],)

        if 'journal' not in self.values: self.values['journal'] = ""
        if 'volume' not in self.values: self.values['volume'] = ""
        if 'pages' not in self.values: self.values['pages'] = ""
        if 'month' not in self.values: self.values['month'] = ""
        if 'year' not in self.values: self.values['year'] = ""
        if 'doi' not in self.values: self.values['doi'] = ""

        return '''
        <div class="paper journal">
            <span class="title">{title}</span><br />
            <span class="authors">{author}</span><br />
            <span class="venue">{journal}, {volume}{number}:{pages}</span>
            <span class="date">{month}, {year}</span><br />
            <span class="doi">{doi}</span>
        </div>'''.format(**self.values)
            

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

    def as_html(self):
        if 'pages' not in self.value: self.values['pages'] = ''
        else:
            self.values['pages'] = ", %s" % (self.values['pages'],)
        if 'address' not in self.values: self.values['address'] = ''
        else:
            self.values['address'] = ". %s" % (self.values['address'],)
        if 'month' not in self.values: self.values['month'] = ""
        if 'year' not in self.values: self.values['year'] = ""
        if 'doi' not in self.values: self.values['doi'] = ""

        return '''
        <div class="paper conference">
            <span class="title">{title}</span><br />
            <span class="authors">{author}</span><br />
            <span class="venue">{booktitle}{pages}{address}</span>
            <span class="date">{month}, {year}</span><br />
            <span class="doi">{doi}</span>
        </div>'''.format(**self.values)

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


    def as_html(self):
        return '''
        <div class="paper patent">
            <span class="title">{title}</span><br />
            <span class="authors">{author}</span><br />
            <span class="number">{number}</span>
            <span class="date">{day} {month}, {year}</span><br />
            <span class="url">{url}</span>
        </div>'''.format(**self.values)

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

    def as_html(self):
        if 'url' not in self.values: self.values['url'] = ''
        if 'month' not in self.values: self.values['month'] = ''
        else: self.values['month'] += ' '

        return '''
        <div class="paper patent">
            <span class="title">{title}</span><br />
            <span class="authors">{author}</span><br />
            <span class="number">{number}</span>
            <span class="institution">{institution}</span>
            <span class="date">{month}{year}</span><br />
            <span class="url">{url}</span>
        </div>'''.format(**self.values)

RECORDTYPES = {
    'article': Article,
    'inproceedings': InProceedings,
    'patent': Patent,
    'techreport': TechReport,
    }
    
_complete_re = re.compile("^\}$")
_entry_re = re.compile("@(?P<entry>\w+)\{(?P<label>.+),$")
_field_re = re.compile("(?P<key>\w+)\s*=\s*(?P<value>.*)$")
def parse(args, strings={}):
    verbose = False
    records = {}
    for inp in args:
        with open(inp) as inf:
            cnt = 0
            for line in map(lambda l:l.strip(), inf.readlines()):
                cnt += 1
                if verbose:
                    print("[%s:%d]: '%s'" % (inp, cnt, line))
                try:
                    if len(line) == 0: continue

                    m = _complete_re.match(line)
                    if m:
                        record.value = record.value.rstrip(",")
                        record.values[record.key] = strings.get(record.value, record.value)
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
                        record.value = record.value.rstrip(",")
                        record.values[record.key] = strings.get(
                            record.value, record.value)
                        record.key = m.group("key")
                        record.value = m.group("value")
                    else: record.value += " "+line

                except Exception as err:
                    print("[%s:%d]: %s\n"
                          "EXC: %s" % (inp, cnt, line, err),
                        file=sys.stderr)
                    sys.exit(1)

            record.value = record.value.rstrip(",")
            record.values[record.key] = strings.get(record.value, record.value)
            
    return records

_string_re = re.compile("^@string\{(?P<key>\w+)=(?P<value>.*)\}$")
def parse_strings(inp):
    strings = {}
    with open(inp) as inf:
        for line in map(lambda l:l.strip(), inf.readlines()):
            m = _string_re.match(line)
            if m:
                key, value = m.group("key"), m.group("value")
                if key in strings:
                    raise Exception("collision! key=%s # %s" % (
                        key,strings.key,))
                strings[key] = value
    return strings    

if __name__ == '__main__':
    ## option parsing    
    pairs = [ "h/help", "o:/output=", "s:/strings=",
              "/header=", "/footer=",
              "/journals=", "/conferences=", "/workshops=", "/patents=", "/techreports=", 
              ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    output = sys.stdout
    strings = None
    h_page = open(HEADER)
    f_page = open(FOOTER)
    h_journals = open(H_JOURNALS)
    h_conferences = open(H_CONFERENCES)
    h_workshops = open(H_WORKSHOPS)
    h_patents = open(H_PATENTS)
    h_techreports = open(H_TECHREPORTS)
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-o", "--output"): output = open(a, "w+a")
            elif o in ("-s", "--strings"): strings = a
            
            elif o in ("--header"): h_page = open(a)
            elif o in ("--footer"): f_page = open(a)
            elif o in ("--journals"): h_journals = open(a)
            elif o in ("--conferences"): h_conferences = open(a)
            elif o in ("--workshops"): h_workshops = open(a)
            elif o in ("--patents"): h_patents = open(a)
            elif o in ("--techreports"): h_techreports = open(a)
            else: raise Exception("unhandled option")
    except Exception as err: die_with_usage(err, 3)

    ## parse input
    if strings: strings = parse_strings(strings)
    if len(args) == 0: die_with_usage("no input file given")
    records = parse(args, strings).values()

    ## output as directed
    def out(s): print(s, file=output)
    def outrs(rs): list(map(lambda r:out(r.as_html()), rs))
    def outt(f): out("".join(f.readlines()).strip())
    
    outt(h_page)
    outt(h_journals)
    outrs(filter(lambda r:r.source.endswith("-journal.bib"), records))
    outt(h_conferences)
    outrs(filter(lambda r:r.source.endswith("-conference.bib"), records))
    outt(h_workshops)
    outrs(filter(lambda r:r.source.endswith("-workshop.bib"), records))
    outt(h_patents)
    outrs(filter(lambda r:r.source.endswith("-patents.bib"), records))
    outt(h_techreports)
    outrs(filter(lambda r:r.source.endswith("-techreport.bib"), records))
    outt(f_page)
