#!/usr/bin/env python3
#
# Replacement for standard UNIX cal utility, supporting date ranges, and
# defaulting to Monday as first day-of-week.
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

import sys, calendar, getopt, datetime

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s: <options> <dates...> where available <options> are:
  -h/--help           : print this message
  -n/--nohilight      : turn off highlighting
  -t/--today <today>  : set <today=YYYY-MM-DD> for highlighting
  -y/--year           : interpret arguments as years
  -c/--columns <n>    : format calendar across <n> columns
  -s/--separator <s>  : format calendar using <s> as month separator
  -f/--firstday <d>   : format calendar with <d> as first day-of-week
and <dates> are formatted as:
  <n>                 : month <n> if 1 <= n <= 12, else year <n>
  <m>/<y>             : month <m> in year <y>
  <m1>-<m2>           : months from <m1> to <m2>, inclusive
  <y1>-<y2>           : years from <y1> to <y2>, inclusive
  <m1>-<m2>/<y>       : months from <m1> to <m2> in year <y>, inclusive
  <m1>/<y1>-<m2>/<y2> : months from <m1> in year <y1> to <m2> in <y2>
for day <d> either 1-7, Monday-Sunday, or abbreviation thereof;
    month <m> either 1-12, January-December, or abbreviation thereof; and
    year <y> is fully qualified, ie., 20 is year 20, not 2020.

Defaults to printing current month, with Monday as first day-of-week.
    """ % (err, sys.argv[0]))
    sys.exit(code)

Year = Month = Date = None

Months = [ '',
           'january', 'february', 'march', 'april', 'may', 'june',
           'july', 'august', 'september', 'october', 'november', 'december' ]
Days = [ '',
         'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
         'saturday', 'sunday' ]

def _format(f, s):
    if nohilight or len(s.strip()) == 0: return s
    else:
        return '\x1b[0%s%s\x1b[0m' % (f,s)

def bold(s): return _format(';1m', s)
def standout(s): return _format(';1;7m', s)
def underline(s): return _format(';4m', s)

def lookup(l, i):
    if i.isdigit(): return int(i)

    for j in range(max(map(len,l)),0,-1):
        ls = list(map(lambda s:s[:j], l))
        if i in ls: return ls.index(i)

    raise Exception("unknown month: %s" % (i,))

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
    year = month = None
    while len(ms) > ncols:
        mss = [ m.split("\n") for m in ms[:ncols] ]
        ms  = ms[ncols:]

        for i in range(ncols):
            mss[i] += ['']*(len(mss[i]) % 8)
            if len(mss[i][0].strip().split()) > 0:
                month, year = mss[i][0].strip().split()
            mss[i][0] = bold(mss[i][0].strip().center(20))
            mss[i][1] = underline(mss[i][1].ljust(20))

            for j in range(1,8):
                m = mss[i][j].split()
                if (year == Year
                    and Date in m
                    and Months.index(month.lower()) == int(Month)
                    ):

                    ## only pad front for first line
                    if j == 2: newm = ['  '] * (7-len(m))
                    else: newm = [ ]

                    for d in m:
                        if d == Date: d = standout("%02s" % d)
                        else: d = "%02s" % d
                        newm.append(d)

                    ## OSX10.6 upgrade change?  ljust() started treating escape
                    ## chars as real chars (ie., can't do 20 for both higlighted
                    ## and unhighlighted).
                    mss[i][j] = ' '.join(newm).ljust(32)

                else:
                    mss[i][j] = mss[i][j].ljust(20)

        for i in range(8):
            for m in mss: yield "%s%s" % (m[i], sep)
            yield "\n"

if __name__ == '__main__':
    ## option parsing
    pairs = [ "h/help", "y/year", "n/nohilight",
              "c:/columns=", "s:/separator=", "f:/firstday=", "t:/today=", ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    ncols = 3
    sep = ' '*4
    fullyear = False
    today = datetime.date.today()
    nohilight = False
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-y", "--year"): fullyear = True
            elif o in ("-c", "--columns"): ncols = int(a)
            elif o in ("-s", "--separator"): sep = a
            elif o in ("-n", "--nohilight"): nohilight = True
            elif o in ("-t", "--today"):
                y,m,d = map(int, a.split("-"))
                today = datetime.date(y,m,d)
            elif o in ("-f", "--firstday"):
                d = int(lookup(Days, a.lower()))
                if not (1 <= d <= 7):
                    raise Exception("bad first day-of-week %s; "
                                    "must be 1 (Monday) to 7 (Sunday)" % d)
                calendar.setfirstweekday(d-1)
            else: raise Exception("unhandled option")
    except Exception as err: die_with_usage(err, 3)

    Year, Month, Date = datetime.date.isoformat(today).split("-")[0:3]
    Date = Date.lstrip('0')

    ## compute the months to print
    months = []
    if len(args) == 0: args = [ Month ]
    for a in args:
        if fullyear: sy,sm, ey,em = int(a),1, int(a),12
        else:
            s,e = a,a
            if "-" in a: s,e = a.split("-")

            em,ey = e,int(Year)
            if "/" in e: em,ey = e.split("/")
            try: em = lookup(Months, em)
            except Exception as err: die_with_usage(err, 4)

            sm,sy = s,ey ## start year is end year if only latter given
            if "/" in s: sm,sy = s.split("/")
            try: sm = lookup(Months, sm)
            except Exception as err: die_with_usage(err, 5)

            ## fix up if no month is given, only year or year range
            if sm > 12 or em > 12: sy,ey = sm,em ; sm,em = 1,12

        months.extend(list(range_months(int(sy),int(sm), int(ey),int(em))))

    ## format and print computed months
    for line in format_months(months, ncols, sep): print(line, end="")
