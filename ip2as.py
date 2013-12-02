#!/usr/bin/env python3
#
# This is a C to Python translation of the corresponding functionality
# in the 'NANOG traceroute' ('traACESroute').  See
# ftp://ftp.aces.com/pub/software/traceroute/ for details.
#
# This Python implementation is:
#
# Copyright (C) 2002 Richard Mortier <mort@cantab.net>.  All Rights
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

import sys, socket, re, pprint, getopt, os, errno

BUF_SZ = 8192

RA_SERVER  = 'whois.ra.net'
RA_SERVICE = '43' ## 'whois'
DATA_DELIM = 'origin:'
RT_DELIM   = 'route:'
PFX_DELIM  = '/'

def die_with_usage(err="", code=0):

    print("""ERROR: %s
Usage: %s [ options ] <names> where [options] are:
    -h|--help    : Help
    -q|--quiet   : Be quiet (minimalist output)
    -v|--verbose : Be verbose
    -V|--VERBOSE : Be very verbose

    -n|--natural : Force natural masks for old-style lookups

    Resolves the given names to their addresses and owning ASs.""" % (
              err, os.path.basename(sys.argv[0]),),
          file=sys.stderr)
    sys.exit(code)

def pfx2id(s):
    pfx, plen = s.split('/')
    pfx = list(map(int, pfx.split('.')))
    plen = int(plen)

    p = 0
    for i in range(len(pfx)):
        p = (p << 8) | pfx[i]
    p = p << (8 * (4-len(pfx)))

    return (p, plen)

def str2id(str):
    quads = str.split('.')
    ret   = (int(quads[0]) << 24) + (int(quads[1]) << 16) + \
            (int(quads[2]) <<  8) + (int(quads[3]) <<  0)
    return ret

def id2str(id):
    return "%d.%d.%d.%d" %\
           (int( ((id & 0xff000000) >> 24) & 0xff),
            int( ((id & 0x00ff0000) >> 16) & 0xff),
            int( ((id & 0x0000ff00) >>  8) & 0xff),
            int( (id  & 0x000000ff)        & 0xff) )

def lookup(net):
    rvs = []
    ra_addr = socket.gethostbyname(RA_SERVER)
    if VERBOSE > 2: print("ra_addr:", ra_addr)
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sp = int(RA_SERVICE) ## socket.getservbyname(RA_SERVICE, 'tcp')

    so.connect((ra_addr, sp))
    so.send(bytes(net + '\r\n', 'ascii'))

    reply = ''
    while 1:
        rbuf = so.recv(BUF_SZ)
        if len(rbuf) == 0: break;
        reply += rbuf.decode('ascii')

    if VERBOSE > 2: pprint.pprint(reply)

    reply = reply.strip().split('\n\n')
    for entry in reply:
        entry = entry.split('\n')

        rv = {}
        last_key = None
        fld_re = re.compile('(^[a-z-]+:){0,1}(.*)')
        for line in entry:
            m = fld_re.match(line)
            if m:
                if m.group(1):
                    key = m.group(1)[:-1]   # remove trailing ':'
                    last_key = key
                else:
                    key = last_key

                val = m.group(2).strip()
                try: rv[key].append(val)
                except: rv[key] = [val]
        rvs.append(rv)

    return rvs

if __name__ == '__main__':

    FORCE_NATURAL_MASK = 0
    VERBOSE = 1
    ip_addrs = None

    ## option parsing
    pairs = [ "h/help", "q/quiet", "v/verbose", "V/VERBOSE", "n/natural",
              "w:/whois=", "i:/input=", ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    try:
        for (o, a) in opts:
            if o in ('-h', '--help'): usage()
            elif o in ('-q', '--quiet'): VERBOSE = 0
            elif o in ('-v', '--verbose'): VERBOSE = 2
            elif o in ('-V', '--VERBOSE'): VERBOSE = 3
            elif o in ('-n', '--natural'): FORCE_NATURAL_MASK = 1
            elif o in ('-w', '--whois'): RA_SERVER = a
            elif o in ('-i', '--input'): ip_addrs = open(a)
            else: raise Exception("unhandled option")

    except Exception as err: die_with_usage(err, 3)

    if not ip_addrs:
        ip_addrs = args
        if not ip_addrs: die_with_usage("no addresses!", 4)

    for ip_str in [ s.strip() for s in ip_addrs ]:
        try:
            if  '/' not in ip_str:
                ip_addr = socket.gethostbyname(ip_str)
                addr = str2id(ip_addr)
            else:
                ip_addr = ip_str
                addr, plen = pfx2id(ip_str)
                addr = addr & pow(2, 32) - pow(2, 32-plen)

            if FORCE_NATURAL_MASK:
                if ((addr & 0xff000000) >> 24) >= 192:
                    net = id2str(addr & 0xffffff00)
                elif ((addr & 0xff000000) >> 24) >= 128:
                    net = id2str(addr & 0xffff0000)
                else:
                    net = id2str(addr & 0xff000000)
            else: net = id2str(addr)

            if VERBOSE > 1: print('query string:', net)

            rvs = lookup(net)
            if VERBOSE > 1:
                print(ip_addr, ':')
                pprint.pprint(rvs)

        except socket.error as error:
            if len(error.args) == 1:
                err = 0
                msg = error.args
                sys.stderr.write('error: %s\n' % (" ".join(msg),))
            else:
                (err, msg) = error.args
                sys.stderr.write('%s: %s\n' % (os.strerror(err), msg))

            sys.exit(1)

        # Make sure we only pick the 'best' owners: all those entries
        # who's covering route is as long as the longest covering
        # route

        best_plen = 0
        best      = []
        for rv in rvs:
            if None not in rv:
                for rt in rv['route']:
                    (pfx, plen) = rt.split('/')
                    plen = int(plen)
                    if plen > best_plen:
                        best_plen = plen
                        best = [ rv ]
                    elif plen == best_plen:
                        if rv not in best: best.append(rv)
        if len(best) == 0:
            best = [{'origin': ['UNKNOWN'], 'route': [ip_str]}]
        ass = []
        ass.extend(map(lambda x, ass=ass: ass.extend(x['origin']), best))
        try:
            while 1:
                ass.remove(None)
        except (ValueError):
            pass
        ass = '/'.join(ass)

        if VERBOSE:
            print('name: %s [%s], route: %s, origin: %s' %
                  (ip_str, net, best[0]['route'][0], ass))
        else:
            print(ip_str, net, best[0]['route'][0], ass)
