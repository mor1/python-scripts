#!/usr/bin/env python3

# Copyright (C) 2011 Richard Mortier <mort@cantab.net>. All Rights Reserved.
#
# Licensed under the GPL v3; see LICENSE.md in the root of this distribution or
# the full text at https://opensource.org/licenses/GPL-3.0

# Given set of people's available times, compute number of people that can make
# each slot. Useful for selecting a time for group meetings.

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
