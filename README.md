# Mort's Python Scripts

Some miscellaneous Python scripts, accumulated over decades.

On NixOS, install `direnv` and then:

``` sh
echo "layout python" >| .envrc
direnv allow
```

...to be able to use `pip` in a local virtual environment.

## Miscellaneous

[`bbdb-migrate`]()
: Migrate BBDB v2 to BBDB v6.

[`bberry.py`]() 
: Library to parse RIM Blackberry backup (.IPD) files. Presents as an enumeration of records. If executed, will attempt to print all contacts as v3.0 vCards.

[`bib2json.py`]()
: Convert BibTeX files to JSON. Relies on well-formed and reasonably formatted
input (ie., it's not a fully fledged BibTeX parser). Running it through Emacs
BibTeX-mode's 'validate' and 'format' should suffice.

```sh
    ~/src/python-scripts.git/bib2json.py \
      -s ~/me.git/bibs.git/strings.bib   \
      ~/me.git/bibs.git/rmm-*.bib >| papers.json
```

[`cc4unifdef.py`](cc4unifdef.py)
: Resolve `#ifdef` lines from C code before line counting.

[`filebomb.py`](filebomb.py)/[`forkbomb.py`](forkbomb.py)
: Quick'n'dirty samples of file and fork bombs for Linux.

[`mspst.py`](mspst.py)
: Beginnings of a rudimentary Microsoft PST file parser.

[`skrype.py`](skrype.py)
: Skype log-parser, presenting a sequence of records. If run as script, splices
all .DBB logfiles to print in sequence-number order.

## CLI tools

[`cli/cal.py`](cli/cal.py)
: Replacement for Unix `cal` command: similar output, more options. Highlights
headers and current date. Defaults to Monday as first day-of-week. **Deprecated
in favour of <https://github.com/mor1/ocal>.**

[`cli/num.py`](cli/num.py)
: Print number in selection of useful bases (bin, dec, oct, hex).

[`cli/pytail.py`](cli/pytail.py)
: Simplistic `tail` implementation.

## Network tools

[`network/https.py`](network/https.py)
: Rudimentary webserver supporting HTTPS, for testing.

[`network/ip2as.py`](network/ip2as.py) 
: Lookup the AS owning an IP address, using WHOIS database data. Follows the
`traceroute-nanog` algorithm.

[`network/pcap_bw.py`](network/pcap_bw.py)
: Computes total and all (src, dst) pairs bandwidth given a PCAP trace.
Currently assumes a "cooked Linux" (SLL) format trace captured using `tcpdump -i
any` from a mininet simulation.

[`network/pdump.py`](network/pdump.py)
: Simple example hex raw packet dump, using SOCK_RAW (Linux) or BPF (OSX).

[`network/pypkt.py`](network/pypkt.py)
: Use Linux `SOCK_RAW` to dump the next packet received.

[`network/server.py`](network/server.py)
: Rudimentary web server, for testing.

[`network/socki.py`](network/socki.py):
: Process `netstat -a` output to give sockets per PID.

[`network/tdump2txt.py`](network/tdump2txt.py)
: Filter to pretty print `tcpdump -x` output to the right of the hex input:
ASCII where possible, hex where not.
