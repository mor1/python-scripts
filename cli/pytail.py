import sys

def get_last_bytes(f, n):

    f.seek(-n, 2)
    buf = f.read(n).strip()
    return buf

def get_tail_bytes(f, newlines):

    bsz = 128    
    while 1:
        buf = get_last_bytes(f, bsz)
        if buf.count("\n") < 2: bsz *= 2
        else: break

    while buf.count("\n") > newlines:
        buf = buf[buf.find("\n")+1:]

    return buf

def get_last_line(f): return get_tail_bytes(f, 0)

def get_last_complete_line(f): return get_tail_bytes(f, 1)

if __name__ == '__main__':
    f = open(sys.argv[1], "rb")
    print get_last_complete_line(f)
    f.close()
