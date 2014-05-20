import http_server, custom, tools, leveldb, blockchain
#Sometimes peers ask us for information or push new transactions or blocks to
#us. This file explains how we respond.
def main(dic, DB):
    dic=tools.unpackage(dic)
    def security_check(dic):
        if 'version' not in dic or dic['version']!=custom.version:
            return {'bool':False, 'error':'version'}
        else:
            #we could add security freatures here.
            return {'bool':True, 'newdic':dic}
    def blockCount(dic, DB):
        length=DB['length']
        if length>=0:
            return {'length':length, 'recentHash':DB['recentHash'], 'sigLength':0} 
        else:
            return {'length':-1, 'recentHash':0, 'sigLength':DB['sigLength']}
    def rangeRequest(dic, DB):
        ran=dic['range']
        out=[]
        counter=0
        while len(tools.package(out))<custom.max_download and ran[0]+counter<=ran[1]:
            block=blockchain.db_get(ran[0]+counter, DB)
            if 'length' in block:
                out.append(block)
            counter+=1
        return out
    def txs(dic, DB): return DB['txs']
    def pushtx(dic, DB): 
        DB['suggested_txs'].append(dic['tx'])
        return 'success'
    def pushblock(dic, DB):
        DB['suggested_blocks'].append(dic['block'])
        return 'success'
    funcs={'blockCount':blockCount, 'rangeRequest':rangeRequest, 
           'txs':txs, 'pushtx':pushtx, 'pushblock':pushblock}
    if 'type' not in dic or type(dic['type']) not in [str, unicode]:
        print('dic: ' +str(dic))
        print('type: ' +str(type(dic)))
        return '<p> no type </p>'
    if dic['type'] not in funcs.keys():
        return str(dic['type'])+' is not in the api'
    check=security_check(dic)
    if not check['bool']:
        return check
    return funcs[dic['type']](check['newdic'], DB)
def g(DB): return (lambda dic: main(dic, DB))
def server(DB): return http_server.serve(custom.listen_port, g(DB), g(DB))
