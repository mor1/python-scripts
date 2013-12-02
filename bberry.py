#!/usr/bin/env python3
#
# Copyright (C) 2010 Richard Mortier <mort@cantab.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import sys, struct, re, string, traceback, os

Verbose = False

class BBerryExc(Exception): pass

def err(s):
    if Verbose: print >>sys.stderr, s

def fmtexc(e, with_tb=False):
    tb = traceback.extract_tb(sys.exc_info()[2])
    s = '%s: %s' % (e.__class__.__name__, str(e))
    if with_tb:
        s += '\n%s' % ('\n'.join([ '#   %s@%s:%s' % (filename, lineno, func)
                                   for (filename,lineno,func,_) in tb ]),)
    return s

def isprintable(b):
    return ((b in string.printable)
            and (b == " " or b not in string.whitespace))

def btos(bs, ascii=False):
    if bs == None or bs == "": return ""
    def _fmt(b):
        if ascii and isprintable(chr(b)): return chr(b)
        return '%0.2x' % (b,)
    return '.'.join(map(_fmt, bs))

def fmtbs(bs, prefix="  : ", ascii=False):
    def _fmt():
        for i in range(0, len(bs), 16):
            yield '\n%s0x%s' % (prefix, btos(bs[i:i+16], ascii))
    return "".join(_fmt())

#
# constants
#

MARKER = b"Inter@ctive Pager Backup/Restore File"
LFVER  = b'\x0A\x02'
NUL    = b'\x00'

NDBS_LEN   = 2
DBN_LEN    = 2
HDR_LEN    = len(MARKER) + len(LFVER) + NDBS_LEN + len(NUL)
REC_OFFSET = 1+2+4
DBHDR_LEN  = 2+4+REC_OFFSET
FHDR_LEN   = 3

AddressBookTypes = {
    1: 'email',
    6: 'work',
    7: 'home',
    8: 'mobile',
    16: 'work2',
    18: 'other',
    32: 'fullname',
    33: 'company',
    35: 'address1',
    36: 'address2',
    38: 'city',
    39: 'state/province',
    40: 'zip/postal code',
    41: 'country',
    42: 'jobtitle',
    55: 'title',
    64: 'notes',
    }

#
# parse harness
#

def contact(rec):
    rv = {}
    for field in rec['fields']:
        ty = AddressBookTypes[field['ty']]
        val = field['val']
        while True:
            try: val = val.decode().strip("\x00")
            except UnicodeDecodeError as e:
                print("val:", val, file=sys.stderr, end='')
                val = val[:e.start]+val[e.end:]
                print(" newval:", val, "\n", file=sys.stderr)
                continue
            break

        if ty not in rv: rv[ty] = val
        else:
            rv[ty] += " %s" % (val,)

    return rv

def parse_fields(f, rlen):
    rv = []
    while rlen > 0:
        bs = f.read(FHDR_LEN)
        if len(bs) == 0: return

        (flen, ftyp) = struct.unpack("<H B", bs)
        bs = f.read(flen)
        rlen -= FHDR_LEN+flen
        field = {'len':flen, 'ty':ftyp, 'val':bs,}
        rv.append(field)
    return rv

def parse_dbrecs(f, ndbs, dbns):
    while True:
        bs = f.read(DBHDR_LEN)
        if len(bs) == 0: break

        (dbid, rlen, dbv, rh, ruid,) = struct.unpack("<H L s H L", bs)
        yield { 'name': dbns[dbid],
                'id': dbid,
                'rlen': rlen,
                'ver': dbv,
                'handle': rh,
                'uid': ruid,
                'fields': parse_fields(f, rlen-REC_OFFSET),
                }

def parse_dbhdrs(f, ndbs):
    dbns = {}
    for i in range(ndbs):
        bs = f.read(DBN_LEN)
        (dbnl, ) = struct.unpack("<H", bs)

        bs = f.read(dbnl)
        (dbn,) = struct.unpack("<%ss" % (dbnl,), bs)

        dbns[i] = dbn[:-1].decode()

    return parse_dbrecs(f, ndbs, dbns)

def parse(f, verbose=False):
    global Verbose
    Verbose = verbose

    bs = f.read(HDR_LEN)
    if len(bs) == 0: raise BBerryExc("bad file! f:%s" % (f.name,))

    (marker, lfver, ndbs, nul) = struct.unpack(
        ">%ss 2s H s" % (len(MARKER),), bs)
    if marker != MARKER: raise BBerryExc("bad marker bs:%s" % (fmtbs(bs),))
    if lfver != LFVER: raise BBerryExc("bad lfver bs:%s" % (fmtbs(bs),))
    if nul != NUL: raise BBerryExc("bad nul bs:%s" % (fmtbs(bs),))

    return { 'marker': marker,
             'lfver': lfver,
             'dbs': parse_dbhdrs(f, ndbs),
             }

def vcard(rec):
    vcard = "BEGIN:VCARD\nVERSION:3.0\n"

    ## contact
    if 'fullname' in rec:
        vcard += 'N:%(fullname)s\n' % rec
        vcard += 'FN:%(fullname)s\n' % rec
    if 'jobtitle' in rec:
        vcard += 'TITLE:%(jobtitle)s\n' % rec
    if 'company' in rec:
        vcard += 'ORG:%(company)s\n' % rec

    if 'address1' in rec:
        rec.setdefault("address1", '')
        rec.setdefault("address2", '')
        rec.setdefault("city", '')
        rec.setdefault("state/province", '')
        rec.setdefault("zip/postal code", '')
        rec.setdefault("country", '')
        vcard += 'ADR:;%(address1)s;%(address2)s;%(city)s;'\
                 '%(state/province)s;%(zip/postal code)s;%(country)s\n' % rec

    ## numbers
    if 'mobile' in rec:
        vcard += 'TEL;TYPE=CELL:%(mobile)s\n' % rec
    if 'home' in rec:
        vcard += 'TEL;TYPE=HOME:%(home)s\n' % rec
    if 'work' in rec:
        vcard += 'TEL;TYPE=WORK:%(work)s\n' % rec
    if 'work2' in rec:
        vcard += 'TEL;TYPE=WORK2:%(work2)s\n' % rec

    ## email
    if 'email' in rec:
        vcard += 'EMAIL;TYPE=INTERNET:%(email)s\n' % rec

    ## note
    if 'notes' in rec:
        vcard += 'NOTE: %(notes)s\n' % rec
    if 'other' in rec:
        vcard += 'NOTE: %(other)s\n' % rec

    vcard += """END:VCARD\n"""
    return vcard

#
# main
#

if __name__ == '__main__':
    ## print specifically contacts as vCards
    with open(sys.argv[1], "rb") as f:
        dbs = parse(f)
        vcards = [ vcard(contact(db)) for db in dbs['dbs'] if db['name'] == 'Address Book' ]
        print(''.join(vcards))
