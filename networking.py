import socket, subprocess, re, tools, custom, urllib, zlib
from time import sleep
from threading import Thread
#This file explains how sockets work for networking.
MAX_MESSAGE_SIZE = 60000
def kill_processes_using_ports(ports):
    popen = subprocess.Popen(['netstat', '-lpn'],
                             shell=False,
                             stdout=subprocess.PIPE)
    (data, err) = popen.communicate()
    pattern = "^tcp.*((?:{0})).* (?P<pid>[0-9]*)/.*$"
    pattern = pattern.format(')|(?:'.join(ports))
    prog = re.compile(pattern)
    for line in data.split('\n'):
        match = re.match(prog, line)
        if match:
            pid = match.group('pid')
            subprocess.Popen(['kill', '-9', pid])
def connect(msg, host, port, time_length=1):
    #print('in connect')
    def func(string, output):
        url=urllib.urlopen(string)
        output[0]=url.read()
    string='http://{}:{}/'.format(host, str(port))
    string+=zlib.compress(msg).encode('hex')
    try:
        output=['error']
        t=Thread(target=func, args=(string, output))
        t.daemon=True
        t.start()
        sleep(time_length)
        t.alive=False
        return tools.unpackage(output[0])
    except:
        #print('ERROR: ' + str(string))
        return {'error':string}
def send_command(peer, msg): 
    msg['version']=custom.version
    return connect(tools.package(msg), peer[0], peer[1])
