#! /usr/bin/env python

#########################################################################
#
# $Id: bbdb-migrate.py,v 1.2 2002/01/10 12:11:36 rmm1002 Exp $

# (C) Richard Mortier (rmm1002@cl.cam.ac.uk), CUCL 2002

# Migrate v2 .bbdb to v6 -- for some reason the bbdb package was
# failing.  Also could serve as a (fairly rubbish) parser for .bbdb
# files.

#
#########################################################################

import sys, string, getopt, fileinput, re

DATE = '2002-01-09'

#########################################################################

if __name__ == '__main__':

    dict = {}

    bbdb_re = re.compile(
        r'^\['                         +
        r'\s*(nil|"[^"]*")'            + # firstname
        r'\s*(nil|"[^"]*")'            + # lastname
        r'\s*(nil|\("[^"]*"\))'        + # aliases
        r'\s*(nil|"[^"]+")'            + # place of work
        r'\s*(nil|\(\[.*\]\))'         + # phone numbers
        r'\s*(nil|\(\[.*\]\))'         + # addresses
        r'\s*(nil|\([^)]+\))'          + # email addresses
        r'\s*(nil|"[^"]+"|\(\(.*\)\))' + # notes, timestamps, etc
        r'\s*nil]$'
        )

    addrs_re = re.compile(r'(\[[^]]+\])\s*')
    zip_re   = re.compile(r'(\d+\]|\([^)]+\)\])')
    addr_re  = re.compile(r'("[^"]*")')
    
    print ';;; file-version: 6'
    print ';;; user-fields: (fax mobile)'

    try:
        for line in fileinput.input():
            match = bbdb_re.match(line)
            if match:
                firstname = match.group(1)
                if firstname != 'nil':
                    firstname = '"' + string.capwords(firstname[1:])
                lastname  = match.group(2)
                if lastname != 'nil':
                    lastname  = '"' + string.capwords(lastname[1:])
                aliases   = match.group(3)
                workplace = match.group(4)
                phones    = match.group(5)
                addresses = match.group(6)
                emails    = match.group(7)
                notes     = match.group(8)

                # munge addresses: street format changed

                new_addrs = ""
                if addresses[0:2] == r'([':
                    addresses = addresses[1:-1]
                    addrs = addrs_re.findall(addresses)

                    for addr in addrs:

                        # get the zip
                        
                        zip_m = zip_re.search(addr)
                        zip = zip_m.group(1)[:-1]
                        zip = string.replace(zip, '"', '')
                        zip = string.replace(zip, '(', '')
                        zip = string.replace(zip, ')', '')
                        zip = '"' + zip + '"'
                        if zip == '"0"':
                            zip = '""'

                        # do other address parts

                        addr_parts = addr_re.findall(addr[1:zip_m.start()])
                        
                        # feed into new_addrs

                        for i in range(3):
                            if addr_parts[i+1] == '""':
                                addr_parts[i+1] = ''
                        new_addrs = new_addrs +\
                                    '[%s (%s %s %s) %s %s ""] ' %\
                                    (addr_parts[0],
                                     addr_parts[1],addr_parts[2],addr_parts[3],
                                     string.join(addr_parts[4:]), zip)

                # munge notes: format changed + add creation-date, timestamp

                if notes[0:2] == '((':
                    notes = notes[:-1] +\
                            ' (creation-date . "%s") (timestamp . "%s"))' %\
                            (DATE, DATE)

                elif notes[0] == '"':
                    notes = '((notes . %s) (creation-date . "%s") (timestamp . "%s"))' %\
                            (notes, DATE, DATE)

                else:
                    notes = '((creation-date . "%s") (timestamp . "%s"))' %\
                            (DATE, DATE)

                # done: print modified line

                if new_addrs == '':
                    new_addrs = 'nil'
                else:
                    new_addrs = '(' + new_addrs + ')'
                val = r'[%s %s %s %s %s %s %s %s nil]' %\
                      (firstname, lastname, aliases, workplace, phones,
                       new_addrs, emails, notes)
                if not dict.has_key(lastname):
                    dict[lastname] = []
                dict[lastname].append(val)
                
            else:
                sys.stderr.write('ERROR: ' + line)

        # can't be arsed doing this right -- this is close enough for now
        
        ks = dict.keys()
        ks.sort()
        for k in ks:
            for l in dict[k]:
                print l
                
    except (KeyboardInterrupt):
        print "interrupted"
        sys.exit(0)

#########################################################################
#########################################################################
