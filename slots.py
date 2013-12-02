#!/usr/bin/env python3
#
# Given set of people's available times, compute number of people that can
# make each slot.  Useful for selecting a time for group meetings.
#
# Copyright (C) 2011 Richard Mortier <mort@cantab.net>.  All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

Days = [ "monday", "tuesday", "wednesday", "thursday", "friday",
         "saturday", "sunday",
         ]

def process(slots, student, times):

    for day in times:
        if day not in slots: slots[day] = {}
        if times[day] == ['-']: continue
        else:
            for time in times[day]:
                if '-' in time:
                    s,e = map(int, time.split('-'))
                else:
                    s,e = int(time), s+100

                for ss in range(s, e, 100):
                    if ss not in slots[day]: slots[day][ss] = []
                    slots[day][ss].append(student)

    return slots

def format(slots, answers):

    string = "Slots:\n%s |" % (" "*4,)
    ts = set()
    for t in [ set(times.keys()) for times in slots.values() ]:
        ts |= t

    s,e = min(ts),max(ts)
    ts = range(s, e+100, 100)
    for t in ts:
        string = "%s %04d |" % (string, t)

    for day in [ d[:2] for d in Days ]:
        if day not in slots: continue

        string = "%s\n%4s |" % (string, day)
        for t in ts:
            n = "%d" % len(slots[day].get(t, []))
            string = "%s %4s |" % (string, " " if n == "0" else n)

    string = "%s\nBest match:" % (string,)
    for a in sorted(answers,
                    key=lambda a: ([d[:2] for d in Days].index(a[1]),a[2])):
        string = "%s\n\t%s %04d [%s]" % (
            string, a[1], a[2], ", ".join(a[3]))

    return string

def select(slots):

    answers = [ (len(ps), day,t, ps)
                for day in slots
                for t,ps in slots[day].items()
                ]
    best = sorted(answers, reverse=True)[0][0]
    answers = filter(lambda a: a[0] == best, answers)
    return answers

if __name__ == '__main__':

    filename = sys.argv[1]

    student = None
    times = {}
    slots = {}

    with open(filename) as f:
        for line in [ l.strip() for l in f ]:
            if len(line) > 0 and line[0] == '#': continue

            es = [ s.strip(":").lower() for s in line.split() ]
            if len(es) > 0 and es[0] in Days:
                times[es[0][:2]] = [ e.strip(", ") for e in es[1:] ]

            else:
                if student: slots = process(slots, student, times)
                student = " ".join(es)
                times = {}

    print(format(slots, select(slots)))
