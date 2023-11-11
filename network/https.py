# Copyright (C) 2010 Richard Mortier <mort@cantab.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#



if __name__ == '__main__': pass



from SocketServer import *
from BaseHTTPServer import *
from SimpleHTTPServer import *
from tlslite.api import *
import string,cgi,time
from os import curdir, sep

PEMFILE = 'server.pem'
s = open(PEMFILE).read() #./server.pem").read()
x509 = X509()
x509.parse(s)
certChain = X509CertChain([x509])


# $ openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes

s = open(PEMFILE).read() ##./server.pem").read()
privateKey = parsePEMKey(s) ##, private=True)

sessionCache = SessionCache()

#class MyHandler(BaseHTTPRequestHandler):
class MyHandler(SimpleHTTPRequestHandler):
    pass
##     def do_POST(self):
##         global rootnode
##         try:
##             ctype, pdict = cgi.parse_header(self.headers.getheader
##             ('content-type'))
##             form = cgi.FieldStorage(fp = self.rfile,
##             headers=self.headers,
##             environ={'REQUEST_METHOD':'POST',
##             'CONTENT_TYPE':self.headers
##             ['content-type']} )


##             if ctype == 'multipart/form-data':

##                 if form.has_key('postdata'):

##                     temp_file = open(form['postdata'].filename,'wb')
##                     buffer = form['postdata'].file.read()
##                     temp_file.write(buffer)
##                     temp_file.close()

##                     self.send_response(200)
## #set apriopriate header if you want send something
## #self.send_header('Content-type',	'text/plain')
##                     self.send_header('Content-type',	'text/html')
##                     self.end_headers()

## #... and send it
## #self.wfile.write('OK')
##                     self.wfile.write('<html><body>Post OK.</body></html>')
##         except :
##             pass
##
class MyHTTPServer(ThreadingMixIn, TLSSocketServerMixIn, HTTPServer):
    def handshake(self, tlsConnection):
        try:
            tlsConnection.handshakeServer(certChain=certChain,
                                          privateKey=privateKey,
                                          sessionCache=sessionCache)
            tlsConnection.ignoreAbruptClose = True
            return True
        except TLSError, error:
            print "Handshake failure:", str(error)
            return False
        
httpd = MyHTTPServer(('0.0.0.0', 8001), MyHandler)
#httpd = MyHTTPServer(('127.0.0.1', 443), MyHandler)
#httpd = HTTPServer(('127.0.0.1', 80), MyHandler)

httpd.serve_forever()

