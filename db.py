from multiprocessing import Process
import os
import json
def default_entry(): return dict(count=0, amount=0)
def main(heart_queue, database_name, logf, database_port):
    import networking
    import sys
    import patricia as patty
    def get(args):
        try:
            return json.loads(patty.get(str(args[0])))
        except:# KeyError:
            return default_entry()
    def put(args): return patty.put(str(args[0]), json.dumps(args[1]))
    def existence(args):
        try:
            patty.get(str(args[0]))
        except:# KeyError:
            return False
        else:
            return True
    def delete(args):
        try:
            patty.delete(str(args[0]))
        except:#we should make sure this is the type of error we are expecting.
            pass
    def proof(args): return patty.prove(args[0])
    def verify(args):#root, key, proof
        return patty.verify(args[0], args[1], args[2])
    def root(args): return patty.root()
    do={'get':get, 'put':put, 'existence':existence, 'delete':delete, 'proof':proof, 'verify':verify, 'root':root}
    def command_handler(command):
        try:
            name = command['type']
            if name not in do.keys(): 
                logf('name: ' +str(name))
                error()
            return do[name](command['args'])
        except Exception as exc:
            logf(exc)
            logf('command: ' + str(command))
            logf('command type: ' + str(type(command)))
            return {'error':'bad data'}
    networking.serve_forever(command_handler, database_port, heart_queue)
