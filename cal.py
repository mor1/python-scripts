#!/usr/bin/env python3.1
#
# Copyright (C) 2010 Richard Mortier <mort@cantab.net>.  All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA 02111-1307, USA.

import sys, calendar, getopt, datetime

Months = [ '',
           'january', 'february', 'march', 'april', 'may', 'june',
           'july', 'august', 'september', 'october', 'november', 'december' ]
Days = [ 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday' ]

def _index(l, i):
    if i.isdigit(): return int(i)

    for j in range(max(map(len,l)),0,-1):
        ls = list(map(lambda s:s[:j], l))
        if i in ls: return ls.index(i)

    assert False, "unknown month: %s" % (i,)

def die_with_usage(err="Usage: ", code=0):
    print(err)
    print("%s: <opts>" % (sys.argv[0], ))        
    sys.exit(code)

def incr_month(y,m):
    m += 1
    if m > 12: y += 1; m = 1
    return y,m

def range_months(sy,sm, ey,em):
    y,m = sy,sm
    while True:
        yield calendar.month(y,m)
        y,m = incr_month(y,m)
        if (y,m) > (ey,em): break
        
def format_months(ms, ncols=3, sep='   '):
    empty_month = [((" "*20)+"\n")*8]

    ms = list(ms)
    ms += empty_month*ncols

    while len(ms) > ncols:
        mss = [ m.split("\n") for m in ms[:ncols] ]
        ms  = ms[ncols:]

        for i in range(ncols):
            mss[i] += ['']*(len(mss[i]) % 8)
            mss[i][0] = mss[i][0].strip().center(20)
            for j in range(8):
                mss[i][j] = mss[i][j].ljust(20)
                
        for i in range(8):
            for m in mss: yield "%s%s" % (m[i], sep)
            yield "\n"
    
if __name__ == '__main__':

    year, month = datetime.date.isoformat(datetime.date.today()).split("-")[0:2]

    shortopts = "hyc:s:f:"
    longopts  = [ "help", "year", "columns=", "separator=", "firstday=" ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    ncols = 3
    sep   = ' '*4
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-y", "--year"): args.append("jan-dec")
            elif o in ("-c", "--columns"): ncols = int(a)
            elif o in ("-s", "--separator"): sep = a
            elif o in ("-f", "--firstday"):
                calendar.setfirstweekday(int(_index(Days, a.lower())))
            else: assert False, "unhandled option"
    except Exception as err: die_with_usage(err, 3)
    
    months = []
    for a in args:
        sm,sy, em,ey = int(month),int(year), int(month),int(year)
        s,e = a,a
        if "-" in a: s,e = a.split("-")

        sm = s
        if "/" in s: sm,sy = s.split("/")
        sm = _index(Months, sm)

        em = e
        if "/" in e: em,ey = e.split("/")
        em = _index(Months, em)

        months.extend(list(range_months(int(sy),int(sm), int(ey),int(em))))
    
    for line in format_months(months, ncols, sep): print(line, end="")
