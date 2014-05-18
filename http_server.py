from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

def serve(port, get, post):
    def fs2dic(fs):
        dic={}
        for i in fs.keys():
            a=fs.getlist(i)
            if len(a)>0:
                dic[i]=fs.getlist(i)[0]
            else:
                dic[i]=""
        return dic
    class MyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type',    'text/html')
            self.end_headers()
            self.wfile.write(get())
        def do_POST(self):
            print("path: " + str(self.path))
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))    
            print(ctype)
            if ctype == 'multipart/form-data' or ctype=='application/x-www-form-urlencoded':    
                fs = cgi.FieldStorage( fp = self.rfile,
                                       headers = self.headers,
                                       environ={ 'REQUEST_METHOD':'POST' })
            else: raise Exception("Unexpected POST request")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(post(fs2dic(fs)))
    ServerClass  = HTTPServer
    Protocol     = "HTTP/1.0"
    server_address = ('127.0.0.1', port)
    httpd = ServerClass(server_address, MyHandler)
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()
empty_page='<html>{}</html>'
def g():
    return empty_page.format('<p>success</p>')
def p(dic):
    print('here')
    return empty_page
serve(8099, g, p)
