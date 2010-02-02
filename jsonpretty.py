#!/usr/bin/env python3.1

import sys, json

if __name__ == '__main__':

    print(json.dumps(json.loads(sys.stdin.read()), indent=4))
