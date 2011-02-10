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
Highlights headers and current date.  Defaults to Monday as first
day-of-week.


ghpy
----

Wrapper to interact with GitHub using REST API.  Currently implements
one command, to retrieve mapping of private collaborators to the
private repositories they collaborate on.


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


skrype
------

Skype log-parser, presenting a sequence of records.  If run as script,
splices all .DBB logfiles to print in sequence-number order.


tdump2txt
--------- 

Filter to pretty print `tcpdump -x` output to the right of the hex
input: ASCII where possible, hex where not.


uontt
-----

Scrape and reformat University of Nottingham timetable website at
<http://nottingham.ac.uk/timetables>. 
Now moved to <http://github.com/mor1/uon/>.
