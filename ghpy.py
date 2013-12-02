#!/usr/bin/env python3.1
#
# Interact with GitHub, eg., retrieve all private collaborators.
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

import sys, json, urllib.request, urllib.parse, pprint, getopt

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s: <options> <commands...> where available <options> are:
  -h/--help           : print this message
  -l/--login <login>  : login account name
  -t/--token <token>  : login token

Currently supported commands:
%s
    """ % (err, sys.argv[0], "\n".join(("  %s: %s" % (c,d[0]) for (c,d) in Commands.items()))))
    sys.exit(code)

## helpers

BASE = "http://github.com/api/v2/json"
def get(u, d=None):
    fp = urllib.request.urlopen(u, d)
    return json.loads(fp.read().decode())

def get_my_repositories(u, d):
    return get("%s/repos/show/%s" % (BASE, u,), d)
def get_org_repositories(u, d):
    return get("%s/organizations/repositories" % (BASE,), d)
def get_organizations(u, d):
    return get("%s/user/show/%s/organizations" % (BASE, u), d)
def get_collaborators(u, r, d):
    return get("%s/repos/show/%s/%s/collaborators" % (BASE, u, r), d)['collaborators']

## function table entries

def my_repositories(login, data):
    repos = get_my_repositories(login, data)
    return " ".join((r['name'] for r in repos['repositories']))

def all_repositories(login, data):
    mrepos = my_repositories(login, data)
    orepos = get_org_repositories(login, data)
    return "%s %s" % (
        " ".join(("<>:%s" % n for n in mrepos.split())),
        " ".join(("%s:%s" % (r['organization'], r['name'])
                  for r in orepos['repositories']))
        )

def all_organizations(login, data):
    repos = get_organizations(login, data)
    return " ".join((r['login'] for r in repos['organizations']))

def all_repository_urls(login, data):
    def _add_credentials(url):
        url = urllib.parse.urlparse(url)
        if url.scheme == 'https':
            netloc = "%s%s@%s" % (
                username, (":%s" % (password,) if password else ""), url.netloc)
            url = (url.scheme, netloc, url.path, url.params, url.query, url.fragment)
        return urllib.parse.urlunparse(url)

    repos = get_repositories(login, data)

    urls = (r['url'] for r in repos['repositories'])
    if username or password: urls = map(_add_credentials, urls)
    return " ".join(urls)

def private_collaborators(login, data):
    repos = get_repositories(login, data)
    collaborators = {}
    for repo in [ r for r in repos['repositories'] if r['private'] ]:
        for c in get_collaborators(login, repo['name'], data):
            if c not in collaborators: collaborators[c] = set()
            collaborators[c].add(repo['name'])

    cs = dict([ (n, list(cs)) for (n,cs) in collaborators.items() ])
    return json.dumps(cs)

Commands = {
    'private-collaborators': ('print JSON-encoded map of collaborators to private repos',
                              private_collaborators),

    'all-repositories': ('print space-separated list of repository names',
                         all_repositories),

    'all-organizations': ('print space-separated list of organizations',
                          all_organizations),

    'all-repository-urls': ('print space-separated list of repository URLs',
                            all_repository_urls),

    }

if __name__ == '__main__':
    ## option parsing
    pairs = [ "h/help",
              "l:/login=", "t:/token=", "u:/username=", "p:/password=", ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    login = None
    token = None
    username = password = None
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-l", "--login"): login = a
            elif o in ("-t", "--token"): token = a
            elif o in ("-u", "--username"): username = a
            elif o in ("-p", "--password"): password = a
            else: raise Exception("unhandled option")
    except Exception as err: die_with_usage(err, 3)
    if not (login or token): die_with_usage()

    ## setup credentials
    data = {}
    if login: data['login'] = login
    if token: data['token'] = token
    data = urllib.parse.urlencode(data)

    ## go!
    for command in args: print(Commands[command][1](login, data))
