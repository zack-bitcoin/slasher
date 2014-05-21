import socket, subprocess, re, tools, custom, urllib, zlib
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
def connect(msg, host, port):
    #print('in connect')
    string='http://{}:{}/'.format(host, str(port))
    string+=zlib.compress(msg).encode('hex')
    try:
        url=urllib.urlopen(string)
        #print('url: ' +str(url))
        return tools.unpackage(url.read())
    except:
        print('ERROR: ' + str(string))
        return {'error':string}
def send_command(peer, msg): 
    msg['version']=custom.version
    return connect(tools.package(msg), peer[0], peer[1])
