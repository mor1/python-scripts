#!/usr/bin/env python2.6
#
# Webscrape the ridiculous UNott timetable website into something
# readable, and provide a useful interface.
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

import sys, getopt, pprint, urllib, textwrap
import simplejson as json

import html5lib
from html5lib import sanitizer
from html5lib import treebuilders
from xml.etree import cElementTree as et

ACTIVITY_TYPES = ['Lecture', 'Computing']
TAG_NS = "http://www.w3.org/1999/xhtml"
TT_URL = "http://uiwwwsci01.ad.nottingham.ac.uk:8003/reporting/Spreadsheet"
## TT_URL = "http://localhost:8003/reporting/Spreadsheet"
MODULES_URL = "Modules;name;%(modules)s?template=SWSCUST+Module+Spreadsheet&weeks=1-52"
COURSES_URL = "Programmes+of+Study;name;%(courses)s?template=SWSCUST+Programme+Of+Study+Spreadsheet&weeks=1-52"

Courses = {
    'cs-bsc-hons': ["Computer Science 3 year UG Full time/1",
                    "Computer Science 3 year UG Full time/2",
                    "Computer Science 3 year UG Full time/3",
                    ],
    'cs-msc-hons': ["Computer Science 4 year UG Full time/1",
                    "Computer Science 4 year UG Full time/2",
                    "Computer Science 4 year UG Full time/3",
                    ],
    }

## : mort@greyjay:~$; curl -v --post302 -i -L -X POST -d"year_id=000110" -d"mnem=G54TCN" 
MODULE_DETAIL_URL = "http://modulecatalogue.nottingham.ac.uk/Nottingham/asp/FindModule.asp"

def tag(t): return "{%s}%s" % (TAG_NS, t)
def spelling(s):
    ## ye gods.
    return s.replace("Activiity", "Activity")

def format_weeks(s):
    def _split(w):
        return map(lambda s: s.replace(" w/c ", "").strip().lstrip("w"),
                   w.split("-"))
    return map(_split, s.split(","))
                                                                          
def format_staff(s):
    ss = s.split()
    if len(ss) <= 2: return "unk"

    surname, initials, title = ss[0], "".join(map(lambda s:s[0], ss[1:-1])), ss[-1]
    return "%s%s" % (initials, surname[0])

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s [modules]: 
  -h/--help            : print this message
  -a/--ascii           : output ASCII
  -j/--json            : output JSON
  --courses            : request for entire courses rather than modules
  --activities [types] : specify comma-separated list of activity types

Activity types defaults to [%s].

Courses shortcuts are [%s].
    """ % (err, sys.argv[0], ", ".join(ACTIVITY_TYPES), ", ".join(Courses.keys())))
    sys.exit(code)

def decode(bytes):
    try: page = bytes.decode("utf8")
    except UnicodeDecodeError, ude:
        page = bytes.decode("latin1")
    return page

def fetch(url, data=None):
    f = urllib.urlopen(url, data, proxies={})
    headers = f.info().items()
    bytes = f.read()
    ct = headers['content-type'] if ('content-type' in headers) else ""
    page = bytes.decode("latin1") if ("charset=ISO-8859-1" in ct) else decode(bytes)
    return (page, headers)

def parse(page):
    parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("etree", et),
                                 tokenizer=sanitizer.HTMLSanitizer)
    return parser.parse(page) 

def scrape_module_details(doc):
    ps = doc.getiterator(tag("p"))
    pprint.pprint([ c.tail for p in ps for c in p.getchildren() if c ])
    
    details = dict([ (c.text.strip().strip(":"),c.tail.strip())
                     for p in ps for c in p.getchildren() if c.text and c.tail ])

    return details

def scrape_timetable(doc):
    modules = []
    module = {}
    tables = doc.getiterator(tag("table"))
    for table in tables:
        attrs = set(table.items())
        if attrs == set([ ("width", "100%"), ("border", "0"), ]):
            ## denotes end of timetable block and possible start of new heading
            if len(module) > 0:
                modules.append(module)
                module = {}

            bolds = list(table.getiterator(tag("b")))
            if len(bolds) == 0: continue ## not a heading 

            module_title = bolds[0].text
            if module_title.startswith("Module:"):
                (_, code, title) = module_title.split("  ")
                module['title'] = title
                module['code'] = code
            elif module_title.startswith("Programme:"):
                module['title'] = module_title.lstrip("Programme: ")
                module['code'] = ""
            else: continue

            module['acts'] = {}
            
        elif attrs == set([ ("cellspacing", "0"), ("cellpadding", "2%"), ("border", "1"), ]):
            ## timetable block
            
            rows = list(table.getiterator(tag("tr")))
            hrow = map(lambda e:spelling(e.text), rows[0].getchildren())
            for row in rows[1:]:
                activity = dict(zip(hrow, map(lambda c:c.text, row)))
                if activity['Name of Type'] not in activity_types: continue

                a = activity["Activity"]
                if a not in module['acts']:
                    module['acts'][a] = dict(map(lambda (k,v): (k,[v]), activity.items()))
                else:
                    for (k,v) in activity.items():
                        if v not in module['acts'][a][k]: module['acts'][a][k].append(v)

        else: pass
    
    return modules

if __name__ == '__main__':

    ## option parsing    
    pairs = [ "h/help", "j/json", "a/ascii", "/courses", "d/detail",
              "/activities=", 
              ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError, err: die_with_usage(err, 2)

    activity_types = ACTIVITY_TYPES
    specify_courses = module_detail = None
    details = courses = modules = None
    dump_json = False
    dump_ascii = False
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-a", "--ascii"): dump_ascii = True
            elif o in ("-j", "--json"): dump_json = True
            elif o in ("--courses",): specify_courses = True
            elif o in ("--activities",): activity_types = a.split(",")
            elif o in ("--detail", "-d"): module_detail = True
            else: raise Exception("unhandled option")
    except Exception, err: die_with_usage()

    if not (dump_ascii or dump_json): dump_ascii = True
    if "".join(map(lambda s:s.lower(), args)) in Courses:
        courses = "%0D%0A".join(map(urllib.quote_plus, Courses[args[0]]))
    elif specify_courses:
        courses = "%0D%0A".join(map(urllib.quote_plus, args))

    if courses:
        url = "%s;%s" % (TT_URL, COURSES_URL % { "courses": courses, })
    else:
        modules = "%0D%0A".join(args)
        url = "%s;%s" % (TT_URL, MODULES_URL % { "modules": modules, })

    ## fetch module data, with details if desired
    if not (courses or modules): die_with_usage("", 1)
    modules = scrape_timetable(parse(fetch(url)[0]))

    if module_detail:
        durl = MODULE_DETAIL_URL
        for m in modules:
            data = { 'year_id': '000110',
                     'mnem': m['code'],
                     }
            page, hdrs = fetch(durl, urllib.urlencode(data))
            m['detail'] = scrape_module_details(parse(page))
                     

    ## dump scraped data; yes, i know i should factor out formatting
    ## and output
    if dump_ascii:
        for module in modules:
            print module['code'], "--", module['title']
            for (act, data) in sorted(module['acts'].items()):
                print "\t%-13s" % (act,), \
                      "%s %5s--%5s" % (data['Day'][0][:2], data['Start'][0], data['End'][0],), \
                      "%-16s" % (data['Room'][0],), \
                      "[ %s ]" % ("; ".join(map(format_staff, data['Staff']))), \
                      "(weeks", 
                weeks = format_weeks(data['Weeks'][0])
                for week in weeks:
                    if len(week) == 4:
                        print "%02d-%02d," % (int(week[0]), int(week[2])),
                    elif len(week) == 2:
                        print "%02d," % (int(week[0]),),
                print ")"
            if 'detail' in module:
                try:
                    for k in ('Knowledge and Understanding',
                              'Professional Skills',
                              'Intellectual Skills',
                              'Transferable Skills',
                              'Education Aims',
                              ):
                        if k not in module['detail']:
                            module['detail'][k] = ""
                    s = """
        %(Level)s.  Credits:%(Total Credits)s.

        \x1b[0;1mTarget Students:\x1b[0m
        %(Target Students)s

        \x1b[0;1mAims:\x1b[0m
        %(Education Aims)s

        \x1b[0;1mResults:\x1b[0m
        %(Knowledge and Understanding)s

        \x1b[0;1mSkills:\x1b[0m
        %(Professional Skills)s %(Intellectual Skills)s %(Transferable Skills)s
""" % module['detail']
                    print textwrap.fill(s, subsequent_indent="\t", replace_whitespace=False)
                except KeyError, ke:
                    print "%s.\n%s" % (ke, pprint.pformat(module['detail']))
                         
    elif dump_json:
        print json.dumps(modules)
