#!/usr/bin/python
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from select import epoll, EPOLLIN, EPOLLET

def brint(*args, **kwds):
    """Prints stuff in bold"""
    color = kwds.get('color', '1m')
    string = "\033[" + color + ' '.join(['{!s}']*len(args)) + "\033[0m"
    print string.format(*args)

brint('creating listening socket')
s = socket()
sfd = s.fileno()
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
brint('binding it to http://localhost:8080')
s.bind(('',8080))
brint('Setting connection queue size to 5')
s.listen(5)
brint('making it non blocking')
s.setblocking(0)
print ''
brint('creating response text')
### javascript in html!
text = """\
<html>
<body>
<canvas id="myCanvas" width="200" height="100" style="border:1px solid #c3c3c3;">
fuck your browser.
</canvas>

<script>

var c=document.getElementById("myCanvas");
var ctx=c.getContext("2d");
ctx.fillStyle="#FF0000";
ctx.fillRect(0,0,150,75);

</script>

</body>
</html>
"""
response = 'HTTP/1.0 200 OK\r'
headers = '''\
Content-Type: text/html\r
Content-Length: %d\r
\r
''' % len(text)
print ''
brint('creating epoll object for efficient polling')
ep = epoll()
brint('registering listening socket with EPOLLIN|EPOLLET')
FLAGS = EPOLLIN|EPOLLET
ep.register(sfd, FLAGS)
print ''
brint('creating file descriptor -> socket object mapping')
fd2sock = {}
try:
    while True:
        print ''
        brint('polling file descriptors')
        events = ep.poll()
        brint('handling events')
        for fd, event in events:
            if fd == sfd and event&EPOLLIN:
                brint("Accepting queued connections...")
                try:
                    while True:
                        c, a = s.accept()
                        brint(' '*3,a)
                        c.setblocking(0)
                        cfd = c.fileno()
                        fd2sock[cfd] = c
                        ep.register(cfd, FLAGS)
                except:
                    continue
            elif event&EPOLLIN:
                brint('handling a client connection')
                msg = bytearray()
                c = fd2sock[fd]
                brint('timeout: ', c.gettimeout())
                try:
                    brint('reading data from client')
                    msg.extend(c.recv(4096))
                except:
                    brint('data not ready')
                    continue
                brint("'''")
                brint(msg, color="1;31m")
                brint("'''")
                brint('sending first line')
                c.send(response)
                brint('sending headers')
                c.send(headers)
                brint('sending body')
                c.send(text)
                brint('closing client connection')
                c.close()
                brint('unregistering client file descriptor from poll')
                ep.unregister(fd)
                brint('removing file desciptor from mapping')
                del fd2sock[fd]
except:
    print '\nshutting down'
    exit()
