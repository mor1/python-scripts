#!/usr/bin/env python3.1

import sys, json, urllib.request, pprint, getopt

def die_with_usage(err="Usage: ", code=0):
    print("""ERROR: %s
%s: <options> <dates...> where available <options> are:
  -h/--help           : print this message
  -l/--login <login>  : 
  -t/--token <token>  : 
    """ % (err, sys.argv[0]))
    sys.exit(code)

## helpers
    
BASE = "http://github.com/api/v2/json"
def get(u, d=None):
    fp = urllib.request.urlopen(u, d)
    return json.loads(fp.read().decode())

def get_repositories(u, d):
    return get("%s/repos/show/%s" % (BASE, u,), d)
def get_collaborators(u, r, d):
    return get("%s/repos/show/%s/%s/collaborators" % (BASE, u, r), d)['collaborators']

## function table entries

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
    'private-collaborators': private_collaborators,
    }

if __name__ == '__main__':
    ## option parsing    
    pairs = [ "h/help",
              "l:/login=", "t:/token=", ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    login = None
    token = None
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-l", "--login"): login = a
            elif o in ("-t", "--token"): token = a
            else: raise Exception("unhandled option")
    except Exception as err: die_with_usage(err, 3)
    
    ## setup credentials
    data = {}
    if login: data['login'] = login
    if token: data['token'] = token
    data = urllib.parse.urlencode(data)

    ## go!
    for command in args: print(Commands[command](login, data))
