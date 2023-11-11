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

## messy.  start at root:nbtref and construct node btree; ditto at
## root:bbtref and construct block btree.  can then walk from
## root:nbtref to recover all blocks including data blocks.  stitching
## these together gives higher layer structures? == messages?

## just trying to read flat leads to problems - can get pages ok, but
## data blocks are variable size with size info in trailer so we need
## to know how big they are in advance, via {node, block} btree
## structures.

import sys, struct, re, string, traceback, os, pprint
ppf = pprint.pprint

Verbose = False

class PSTExc(Exception): pass

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

HDR_LEN = 4+4+2+2+2+1+1+4+4
U_HDR_LEN = 8+8+4+128+8+72+4+128+128+1+1+2+8+4    +3+1+32
A_HDR_LEN =   4+4+4+128  +40  +128+128+1+1+2    +8+4+3+1+32
PAGE_LEN = 512
FIRST_AMAP_OFFSET = 0x4400
SUCC_AMAP_OFFSET = 253952-PAGE_LEN

MAGIC = b'!BDN'
MAGIC_CLIENT = b'\x53\x4D'
PLATFORM_CREATE = b'\x01'
PLATFORM_ACCESS = b'\x01'

Crypt_methods = {
    0x00: 'none',
    0x01: 'permute',
    0x02: 'cyclic',
    }

Versions = {
    15: 'ansi',
    23: 'unicode',
    }

AMap_valids = {
    0x00: 'invalid',
    0x01: 'valid (deprecated)',
    0x02: 'valid',
    }

Page_types = {
    0x80: 'block BTree page',
    0x81: 'node BTree page',
    0x82: 'free map page',
    0x83: 'allocation page map page',
    0x84: 'allocation map page',
    0x85: 'free page map page',
    0x86: 'density list page',
    }
for (k,v) in [ (k,v) for (k,v) in Page_types.items() ]: Page_types[v] = k

Uncrypt_values = {
    0x47, 0xf1, 0xb4, 0xe6, 0x0b, 0x6a, 0x72, 0x48,
    0x85, 0x4e, 0x9e, 0xeb, 0xe2, 0xf8, 0x94, 0x53, # 0x0f

    0xe0, 0xbb, 0xa0, 0x02, 0xe8, 0x5a, 0x09, 0xab,
    0xdb, 0xe3, 0xba, 0xc6, 0x7c, 0xc3, 0x10, 0xdd, # 0x1f

    0x39, 0x05, 0x96, 0x30, 0xf5, 0x37, 0x60, 0x82,
    0x8c, 0xc9, 0x13, 0x4a, 0x6b, 0x1d, 0xf3, 0xfb, # 0x2f

    0x8f, 0x26, 0x97, 0xca, 0x91, 0x17, 0x01, 0xc4,
    0x32, 0x2d, 0x6e, 0x31, 0x95, 0xff, 0xd9, 0x23, # 0x3f

    0xd1, 0x00, 0x5e, 0x79, 0xdc, 0x44, 0x3b, 0x1a,
    0x28, 0xc5, 0x61, 0x57, 0x20, 0x90, 0x3d, 0x83, # 0x4f

    0xb9, 0x43, 0xbe, 0x67, 0xd2, 0x46, 0x42, 0x76,
    0xc0, 0x6d, 0x5b, 0x7e, 0xb2, 0x0f, 0x16, 0x29, # 0x5f

    0x3c, 0xa9, 0x03, 0x54, 0x0d, 0xda, 0x5d, 0xdf,
    0xf6, 0xb7, 0xc7, 0x62, 0xcd, 0x8d, 0x06, 0xd3, # 0x6f

    0x69, 0x5c, 0x86, 0xd6, 0x14, 0xf7, 0xa5, 0x66,
    0x75, 0xac, 0xb1, 0xe9, 0x45, 0x21, 0x70, 0x0c, # 0x7f

    0x87, 0x9f, 0x74, 0xa4, 0x22, 0x4c, 0x6f, 0xbf,
    0x1f, 0x56, 0xaa, 0x2e, 0xb3, 0x78, 0x33, 0x50, # 0x8f

    0xb0, 0xa3, 0x92, 0xbc, 0xcf, 0x19, 0x1c, 0xa7,
    0x63, 0xcb, 0x1e, 0x4d, 0x3e, 0x4b, 0x1b, 0x9b, # 0x9f

    0x4f, 0xe7, 0xf0, 0xee, 0xad, 0x3a, 0xb5, 0x59,
    0x04, 0xea, 0x40, 0x55, 0x25, 0x51, 0xe5, 0x7a, # 0xaf

    0x89, 0x38, 0x68, 0x52, 0x7b, 0xfc, 0x27, 0xae,
    0xd7, 0xbd, 0xfa, 0x07, 0xf4, 0xcc, 0x8e, 0x5f, # 0xbf

    0xef, 0x35, 0x9c, 0x84, 0x2b, 0x15, 0xd5, 0x77,
    0x34, 0x49, 0xb6, 0x12, 0x0a, 0x7f, 0x71, 0x88, # 0xcf

    0xfd, 0x9d, 0x18, 0x41, 0x7d, 0x93, 0xd8, 0x58,
    0x2c, 0xce, 0xfe, 0x24, 0xaf, 0xde, 0xb8, 0x36, # 0xdf

    0xc8, 0xa1, 0x80, 0xa6, 0x99, 0x98, 0xa8, 0x2f,
    0x0e, 0x81, 0x65, 0x73, 0xe4, 0xc2, 0xa2, 0x8a, # 0xef

    0xd4, 0xe1, 0x11, 0xd0, 0x08, 0x8b, 0x2a, 0xf2,
    0xed, 0x9a, 0x64, 0x3f, 0xc1, 0x6c, 0xf9, 0xec, # 0xff
    }

def encrypt_permute(bs): return list(map(lambda b: Uncrypt_values.index(b), bs))
def decrypt_permute(bs): return list(map(lambda b: Uncrypt_values[b], bs))

def parse_nid(nid):
    nid_t = nid & 0x001f
    nid_i = nid & 0xffe0
    return (nid_t, nid_i)

def parse_bid_u(bid):
    internal = bid & 0x00000002
    index    = (bid & 0xfffffffc) >> 2

    return { 'internal': internal==1,
             'index': index,
             }

def parse_bref_u(bref):
    (bid, ib) = struct.unpack("<QQ", bref)
    return { 'bid': parse_bid_u(bid),
             'ib': ib,
             }

def parse_page_u(bs):
    (data, trailer) = struct.unpack("<496s 16s", bs)
    (pt, ptr, sig, crc, bid) = struct.unpack("<BB 2s L Q", trailer)
    if pt not in Page_parsers_u: raise PSTExc("bad page type pt:%x" % (pt,))

    data = Page_parsers_u[pt](data)
    ppf(("page", data))
    if pt == 0x80: parse_key = parse_nid
    elif pt == 0x81: parse_key = parse_bid_u

    for i in range(len(data['entries'])):
        data['entries'][i]['key'] = parse_key(data['entries'][i]['key'])

    return { 'data': data,
             'type': pt,
             'sig': sig,
             'crc': crc,
             'bid': parse_bid_u(bid),
             }

def parse_bbt_u(bs):
    (bref, bc, rc) = struct.unpack("<16s HH", bs[:20])
    return { 'bref': parse_bref_u(bref),
             'nbytes': bc,
             'refcnt': rc,
             }

def parse_nbt_u(bs):
    (nid, biddata, bidsub, nidparent) = struct.unpack("<QQQL", bs)
    ppf((nid, biddata, bidsub, nidparent))
    return { 'nid': parse_nid(nid),
             'biddata': parse_bid_u(biddata),
             'bidsub': parse_bid_u(bidsub),
             'nidparent': parse_nid(nidparent),
             }

def parse_bt_u(bs):
    (key, bref) = struct.unpack("<Q 16s", bs)
    return { 'key': key,
             'bref': parse_bref_u(bref),
             }

def parse_bth_u(bs):
    (rgentries, nent, nent_max, ent_sz, level,
     _) = struct.unpack("<488s BBBB 4s", bs)
    return (rgentries, { 'nent': int(nent),
                         'nent_max': int(nent_max),
                         'ent_sz': int(ent_sz),
                         'level': int(level),
                         })

def parse_bpage_u(bs):
    (rgentries, rv) = parse_bth_u(bs)

    i, sz, entries = 0, rv['ent_sz'], []
    if rv['level'] == 0:
        while i+sz <= len(rgentries):
            entries.append(parse_bbt_u(rgentries[i:i+sz]))
            i += sz

    else:
        while i+sz <= len(rgentries):
            entries.append(parse_bt_u(rgentries[i:i+sz]))
            i += sz

    rv.update({ 'entries': entries, })
    return rv

def parse_npage_u(bs):
    (rgentries, rv) = parse_bth_u(bs)

    i, sz, entries = 0, rv['ent_sz'], []
    if rv['level'] == 0:
        while i+sz <= len(rgentries):
            entries.append(parse_nbt_u(rgentries[i:i+sz]))
            i += sz

    else:
        while i+sz <= len(rgentries):
            entries.append(parse_bt_u(rgentries[i:i+sz]))
            i += sz

    rv.update({ 'entries': entries, })
    return rv

Page_parsers_u = {
    0x80: parse_bpage_u,
    0x81: parse_npage_u,
    }

def parse_root_u(root):
    (_, file_eof, amap_last, amap_free, pmap_free, nbt, bbt, valid,
     _) = struct.unpack("<L Q Q Q Q 16s 16s B 3s", root)

    return { 'eof': file_eof,
             'amap_last': amap_last,
             'amap_free': amap_free,
             'pmap_free': pmap_free,
             'nbt': parse_bref_u(nbt),
             'bbt': parse_bref_u(bbt),
             'valid': AMap_valids[valid],
             }

def parse_contents(f, h):
    if Versions[h['version']] == 'unicode': parse_page = parse_page_u
    else: raise PSTExc("unknown version! version:%d" % (h['version'],))

    block = get_block_u(f, h['root']['nbt'])
    return [block]


##     f.seek(FIRST_AMAP_OFFSET)
##     bs = f.read(PAGE_LEN)
##     amap = parse_page(bs)
##     yield amap

##     while f.tell() < h['root']['eof']:
##         page = parse_page(f.read(PAGE_LEN))
##         if page['type'] == Page_types['block BTree page']:
##             page['data'] = parse_bpage_u(page['data'])
##         elif page['type'] == Page_types['node BTree page']:
##             page['data'] = parse_npage_u(page['data'])
##         else: BARF

##         yield page

def parse_header(f):
    bs = f.read(HDR_LEN)

    (magic, crc_partial, magic_client, version, version_client,
     platform_create, platform_access, _, _) = struct.unpack("<4s L 2sH Hcc LL", bs)
    if magic != MAGIC: raise PSTExc("bad magic bs:%s" % fmtbs(bs))
    if magic_client != MAGIC_CLIENT: raise PSTExc("bad magic_client bs:%s" % (fmtbs(bs),))
    if platform_create != PLATFORM_CREATE: raise PSTExc("bad platform_create bs:%s" % (fmtbs(bs),))
    if platform_access != PLATFORM_ACCESS: raise PSTExc("bad platform_access bs:%s" % (fmtbs(bs),))

    header = { 'version': version,
               'vclient': version_client,
               'crc': crc_partial,
               }

    if Versions[version] == 'unicode':
        bs = f.read(U_HDR_LEN)
        (_, bid_p, unique, rgnid,
         _, root, align, rgbfm, rgbfp, sentinel, crypt_method,
         _, bid_b, crc_full,
         _) = struct.unpack('<QQ L 128s   Q 72s L 128s 128s BB   HQL   36s', bs)

        header['crc'] = (header['crc']<<4) + crc_full
        root = parse_root_u(root)

    elif Versions[version] == 'ansi':
        bs = f.read(A_HDR_LEN)
        (_, bid_b, bid_p, unique, rgnid, root, rgbfm, rgbfp, sentinel, crypt_method,
         _) = struct.unpack('<Q LLL 128s 40s 128s 128s BB 50s', bs)

    else: raise PSTExc("bad version bs:%s" % (fmtbs(bs),))

    rgnids = tuple(map(parse_nid, struct.unpack("<32L", rgnid)))
    header.update(
        { 'next_page_bid': bid_p,
          'next_bid': bid_b,
          'unique': unique,
          'rgnids': rgnids,
          'root': root,
          'rgbfm': rgbfm,
          'rgbfp': rgbfp,
          'sentinel': sentinel,
          'crypt_method': crypt_method,
          })
    return header

def get_block_u(f, bref):
    offset = bref['ib']
    f.seek(offset)
    bs = f.read(PAGE_LEN)
    page = parse_page_u(bs)

    return { 'bref': bref,
             'offset': offset,
             'page': page,
             }

def parse(f):
    header = parse_header(f)
    return { 'header': header,
             'contents': parse_contents(f, header),
             }

#
# main
#

if __name__ == '__main__':
    with open(sys.argv[1], "rb") as f:
        pst = parse(f)
        h = pst['header']
        ppf(("h", h))

        i = 0
        for page in pst['contents']:
            ppf(('page %d' % i, page))
            i += 1

'''

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

'''
