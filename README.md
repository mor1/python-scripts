Mort's Python Scripts
=====================


bberry
------

Library to parse RIM Blackberry backup (.IPD) files.  Presents as an
enumeration of records.  If executed, will attempt to print all
contacts as v3.0 vCards.


bib2html
--------

Convert BibTeX files to JSON/HTML.  Relies on well-formed and
reasonably formatted input (ie., it's not a fully fledged BibTeX
parser).  Running it through Emacs BibTeX-mode's 'validate' and
'format' should suffice.


cal
---

Replacement for Unix `cal` command: similar output, more options.
Defaults to Monday as first day-of-week.


ip2as
-----

Lookup the AS owning an IP address, using WHOIS database data.
Follows the `traceroute-nanog` algorithm.


jsonpretty
----------

Pretty print JSON taken from `stdin`.


num
---

Print number in selection of useful bases (bin, dec, oct, hex).


tdump2txt
--------- 

Filter to pretty print `tcpdump -x` output to the right of the hex
input: ASCII where possible, hex where not.
