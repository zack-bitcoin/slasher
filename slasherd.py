#!/usr/bin/env python
import networking, sys, tools, custom, time

def main():
    info=sys.argv
    p={'command':sys.argv[1:]}
    if len(p['command'])==0:
        p['command'].append(' ')
    if p['command'][0]=='times':
        times=p['command'][1]
        s=p['command'][2]
        p['command']=p['command'][3:]
        for i in range(int(times)-1):
            time.sleep(float(s))
            print(run_command(p))
    return run_command(p)

def run_command(p):
    peer=['127.0.0.1', custom.slasherd_port]
    response=networking.send_command(peer, p, 5)
    if tools.can_unpack(response):
        response=tools.unpackage(response)
    if type(response)==type({'a':1}):
        if 'error' in response:
            print('slashercoin is probably off. Use command: "python threads.py" to turn it on. (you may need to reboot it a couple times to get it working)')
    return(response)
'''
    if 'error' in response:
        if (response['error'] in ['cannot connect', 'cannot download']) and len(sys.argv)>1 and (sys.argv[1]=='start'):
            print('slashercoin is probably off. Use command: "python threads.py" to turn it on')
            #threads.main()
            sys.exit(1)
    return(response)
'''        
print(main())
