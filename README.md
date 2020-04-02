Mort's Python Scripts
=====================


bberry
------

Library to parse RIM Blackberry backup (.IPD) files. Presents as an enumeration
of records. If executed, will attempt to print all contacts as v3.0 vCards.


bib2json
--------

Convert BibTeX files to JSON. Relies on well-formed and reasonably formatted
input (ie., it's not a fully fledged BibTeX parser). Running it through Emacs
BibTeX-mode's 'validate' and 'format' should suffice.

    ~/src/python-scripts.git/bib2json.py \
      -s ~/me.git/bibs.git/strings.bib   \
      ~/me.git/bibs.git/rmm-*.bib >| papers.json


cal
---

Replacement for Unix `cal` command: similar output, more options. Highlights
headers and current date. Defaults to Monday as first day-of-week.

**Deprecated in favour of <https://github.com/mor1/ocal>.**


filebomb/forkbomb
-----------------

Quick'n'dirty samples of file and fork bombs for Linux.


ghpy
----

Wrapper to interact with GitHub using REST API. Currently implements one
command, to retrieve mapping of private collaborators to the private
repositories they collaborate on.


ip2as
-----

Lookup the AS owning an IP address, using WHOIS database data. Follows the
`traceroute-nanog` algorithm.


jsonpretty
----------

Pretty print JSON taken from `stdin`.

**Deprecated in favour of `... | jq .`.**


num
---

Print number in selection of useful bases (bin, dec, oct, hex).


pcap_bw
-------

Computes total and all (src, dst) pairs bandwidth given a PCAP trace. Currently
assumes a "cooked Linux" (SLL) format trace captured using `tcpdump -i any` from
a mininet simulation.


pdump
-----

Simple example hex raw packet dump, using SOCK_RAW (Linux) or BPF (OSX).


skrype
------

Skype log-parser, presenting a sequence of records. If run as script, splices
all .DBB logfiles to print in sequence-number order.


slots
-----

Given set of people's available times, compute number of people that can make
each slot. Useful for selecting a time for group meetings.


tdump2txt
---------

Filter to pretty print `tcpdump -x` output to the right of the hex input: ASCII
where possible, hex where not.
