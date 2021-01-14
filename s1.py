from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import os
import requests
#import ssl
import time
import cgi
import base64
import hashlib
import datetime
import time
from urllib import parse
import traceback
import math
from threading import Timer,Thread
from lxml import html

num_per_page=24
#hourly_client_quota=dict()#ip->usage
#daily_client_quota=dict()
#client_quota_hour_time=0
#max_hourly_client_quota=int(os.environ.get('CLIENT_QUOTA_HOURLY','200'))#this is for per hour
#max_daily_client_quota=int(os.environ.get('CLIENT_QUOTA_DAILY','1000'))#this is for per hour
#valid_ip_file_dict=dict()
#ban_list=set()

category_list=['chara','scene']

path_mapper=['/chara','/scene','/housing']

title_mapper={
    'chara':['キャラ','人物','人物','Chara'],
    'scene':['シーン','工作室','工作室','Scene'],
    'housing':['ハウジング','房屋','房屋','Housing']
}

key_mapper={
    'chara':
        [{'sex':'性別','height':'身長','breast':'バスト','hair':'髪型','type':'タイプ','order':'順序'},
            {'sex':'性別','height':'身高','breast':'胸部','hair':'髮型','type':'個性','order':'順序'},
            {'sex':'性别','height':'身高','breast':'胸部','hair':'发型','type':'个性','order':'顺序'},
            {'sex':'Gender','height':'Height','breast':'Bust','hair':'Hair','type':'Personality','order':'Order'}],
    'scene':
        [{'order':'順序'},
            {'order':'順序'},
            {'order':'顺序'},
            {'order':'Order'}],
    'housing':
        [{'size':'サイズ','order':'順序'},
            {'size':'大小','order':'順序'},
            {'size':'大小','order':'顺序'},
            {'size':'size','order':'Order'}]
}
value_mapper={
    'chara':
        [
            {'sex':['男','女'],
                'height':['低い','普通','高い'],
                'breast':['小さい','普通','大きい'],
                'hair':['ショート','セミロング','ロング','ポニー','ツイン','その他'],
                'type':['クール','普通','苦労人','女友達','ギャル','気弱','母性的','ドS','オープン','天然'],
                'order':['更新順','投稿順','総合DL数','週間DL数','いいね']},
            {'sex':['男','女'],
                'height':['低','普通','高'],
                'breast':['小','普通','大'],
                'hair':['短','半長','長','馬尾','雙馬尾','其它'],
                'type':['安靜','普通','勤勞','女友感','時髦','膽小','母性','S','開朗','天然'],
                'order':['更新順序','投稿順序','總下載數','當週下載數','讚數']},
            {'sex':['男','女'],
                'height':['低','普通','高'],
                'breast':['小','普通','大'],
                'hair':['短','半长','长','马尾','双马尾','其它'],
                'type':['安静','普通','勤劳','女友感','时髦','胆小','母性','S','开朗','天然'],
                'order':['更新顺序','投稿顺序','总下载数','当周下载数','赞数']},
            {'sex':['Male','Female'],
                'height':['Short','Average','Tall'],
                'breast':['Small','Average','Large'],
                'hair':['Short','Semi-long','Long','Pony','Twin','Other'],
                'type':['Quiet','Average','Hardworking','Girlfriend','Fashionable','Timid','Motherly','Sadistic','Open-hearted','Natural'],
                'order':['Update','Submit','Download','Weekly Download','Like']}
        ],
    'scene':
        [
            {'order':['更新順','投稿順','総合DL数','週間DL数','いいね']},
            {'order':['更新順序','投稿順序','總下載數','當週下載數','讚數']},
            {'order':['更新顺序','投稿顺序','总下载数','当周下载数','赞数']},
            {'order':['Update','Submit','Download','Weekly Download','Like']}
        ],
    'housing':
        [
            {'size':['小','中','大'],'order':['更新順','投稿順','総合DL数','週間DL数','いいね']},
            {'size':['小','中','大'],'order':['更新順序','投稿順序','總下載數','當週下載數','讚數']},
            {'size':['小','中','大'],'order':['更新顺序','投稿顺序','总下载数','当周下载数','赞数']},
            {'size':['Small','Medium','Large'],'order':['Update','Submit','Download','Weekly Download','Like']},
        ]
}
header_order={
    'chara':['sex','height','breast','hair','type'],
    'scene':[],
    'housing':['size']
}

header_style={
    'chara':['"width:200px; height:280px; cursor:pointer"','"width:220px; height:280px; float:right; padding: 0.01em 8px"'],
    'scene':['"width:320px; height:180px; cursor:pointer"','"width:320px; height:180px; padding: 0.01em 8px"'],
    'housing':['"width:320px; height:180px; cursor:pointer"','"width:320px; height:210px; padding: 0.01em 8px"']
}

class PostHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, 'ok')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, HEAD')
        self.end_headers()
        return
        
    def do_HEAD(self):
        self.send_response(200, 'ok')
        self.end_headers()
        return
        
    def do_GET(self):
        ip=self.headers.get('X-Forwarded-For',self.client_address[0])
#        proto=self.headers.get('X-Forwarded-Proto','local')
#        if(proto=='http'):
#            self.send_response(301)
#            self.send_header('Location', 'https:/'+str(os.environ.get('HEROKU_APP_NAME','aisyoujyo'))+'.herokuapp.com'+self.path)
#            self.end_headers()
#            self.connection.close()
        
        #print(self.path)
        print(json.dumps({'ts':int(time.time()),'url':self.path,'ip':ip}))
#        if('@' in self.path):
#            q_string=self.path[self.path.find('@')+1:]
#            q_op=('+' if '+' in q_string else ('-' if '-' in q_string else '*'))
#            q_target,q_value=q_string.split(q_op)
#            q_value=int(q_value)
#            self.path=self.path[:self.path.find('@')]
#            path = parse.urlparse(self.path).path
#            query = parse.urlparse(self.path).query
#            #print(q_op,q_target,q_value)
#            if(len(query)==0):
#                s=dict()
#            else:
#                j=dict([qc.split("=") for qc in query.split("&") if len(qc.split("="))==2])
#                s=dict([k,set(list(map(int,v.split('.'))))] for k,v in j.items() if len(v)>0)
#            if('page' not in s):
#                s['page']=set([1])
#            if(q_target not in s):
#                s[q_target]=set()
#            if(q_target in ['cat']):
#                if(q_op=='*'):
#                    s={'lang':s.get('lang',set([0]))}
#                    path=path_mapper[q_value]
#            elif(q_target in ['order','page','lang']):
#                if(q_op=='*'):
#                    s[q_target]=set([q_value])
#                elif(q_op=='+'):
#                    s[q_target]=set([[*s[q_target]][0]+q_value])
#                elif(q_op=='-'):
#                    if([*s[q_target]][0]>1):
#                        s[q_target]=set([[*s[q_target]][0]-q_value])
#            else:
#                if(q_op=='+'):
#                    s[q_target].add(q_value)
#                elif(q_op=='-'):
#                    s[q_target].remove(q_value)
#    #            else:
#    #                s[q_target]=set([q_value])
#            if(q_target not in ['page','lang']):
#                s['page']=set([1])
#            self.send_response(303)
#            self.send_header('Location', path+'?'+'&'.join([k+'='+'.'.join(list(map(str,v))) for k,v in s.items()]))
#            self.end_headers()
#            self.connection.close()
#            return
        if(self.path[:14]=='/honey2_chara_'):
            self.send_response(200, 'ok')
            self.end_headers()
            self.wfile.write(requests.get('http://honey2-img.s3-ap-northeast-1.amazonaws.com/chara/image'+self.path).content)
            return
            
        elif(self.path[:14]=='/honey2_scene_'):
            self.send_response(200, 'ok')
            self.end_headers()
            self.wfile.write(requests.get('http://honey2-img.s3-ap-northeast-1.amazonaws.com/scene/image'+self.path).content)
            return

#        elif(self.path[:16]=='/honey2_housing_'):
#            self.send_response(200, 'ok')
#            self.end_headers()
#            self.wfile.write(requests.get('http://honey2-img.s3-ap-northeast-1.amazonaws.com/housing/image'+self.path).content)
#            return

        elif(self.path=='/'):
            self.send_response(200, 'ok')
            self.end_headers()
#            s='<!DOCTYPE html><html><title>Honey Select 2 Download</title>'+\
#                '<meta charset="UTF-8"><link rel="stylesheet" href="/w3.css">'+\
#                '<body class="w3-light-grey w3-content" style="max-width:1920px"><div class="w3-main" style="margin-left:50px;margin-right:50px">'+\
#                '<header id="portfolio">'+\
#                '<h1><a href="/chara" style="text-decoration: none;padding: 8px">Chara</a><a href="/scene" style="text-decoration: none;padding: 8px">Scene</a><a href="/housing" style="text-decoration: none;padding: 8px">Housing</a></h1>'+\
#                '</header></div></body></html>'
#            s='<!DOCTYPE html><html><title>Honey Select 2 Download</title>'+\
#                '<meta charset="UTF-8"><link rel="stylesheet" href="/w3.css">'+\
#                '<body class="w3-light-grey w3-content" style="max-width:1920px"><div class="w3-main" style="margin-left:50px;margin-right:50px">'+\
#                '<header id="portfolio">'+\
#                '<h1><a href="/chara" style="text-decoration: none;padding: 8px">Chara</a></h1>'+\
#                '</header></div></body></html>'
#            self.wfile.write(bytes(s,'utf-8'))
            with open('index.html','rb') as f:
                self.wfile.write(f.read())
        elif(self.path=='/favicon.ico'):
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.connection.shutdown(1)
        elif(self.path=='/util.js'):
            self.send_response(200, 'ok')
            self.send_header('Cache-Control', 'max-age=86400')
            self.end_headers()
            with open('util.js','r',encoding='utf-8') as f:
                s=f.read()
            self.wfile.write(bytes(s,'utf-8'))
        elif(self.path=='/w3.css'):
            self.send_response(200, 'ok')
            self.send_header('Cache-Control', 'max-age=86400')
            self.end_headers()
            with open('w3.css','r',encoding='utf-8') as f:
                s=f.read()
            self.wfile.write(bytes(s,'utf-8'))
        else:
            try:
#                if(not check_client_quota(ip)):
#                    self.send_response(200, 'ok')
#                    self.end_headers()
#                    self.connection.close()
#                    return
                parsed=parse.urlparse(self.path)
                query=parsed.query
                path=parsed.path
                category=path[1:]
                j=dict([qc.split("=") for qc in query.split("&") if len(qc.split("="))==2])
                s=dict([k,set(list(map(int,v.split('.'))))] for k,v in j.items() if len(v)>0)
                order=[*s.get('order',[0])][0]
                page=[*s.get('page',[1])][0]
                lang=[*s.get('lang',[0])][0]
                mode=[*s.get('mode',[0])][0]#0=normal, 1=compatible(href instead of cors fetch)
                #print(s)
                r_list=data_list[category][order]
                for k,v in s.items():
                    if(k in set(['page','order','lang','mode'])):
                        continue
                    r_list=[ele for ele in r_list if ele[k] in v]
                target_beg=(page-1)*24
                max_page=math.ceil(len(r_list)/24)
                if(page>max_page):
                    s['page']=set([max_page])
                    self.send_response(303)
                    self.send_header('Location', path+'?'+'&'.join([k+'='+'.'.join(list(map(str,v))) for k,v in s.items()]))
                    self.end_headers()
                    self.connection.close()
                r_list=r_list[target_beg:target_beg+24]
#                add_file_valid(ip,['/upai_'+category+'_'+x['id']+'.png' for x in r_list])
                #f_data=open((str(self.path)[1:] if str(self.path)[0]=='/' else self.path),'rb').read()
                self.send_response(200, 'ok')
                self.end_headers()
                s=('<!DOCTYPE html><html><title>Honey Select 2 '+title_mapper[category][lang]+'</title><meta charset="UTF-8"><link rel="stylesheet" href="/w3.css"><body class="w3-light-grey w3-content" style="max-width:1920px"><script src="util.js"></script><!-- !PAGE CONTENT! --><div class="w3-main" style="margin-left:50px;margin-right:50px"><!-- Header --><header id="portfolio"><h1>'+\
                    ''.join([('<b style="display: inline;text-decoration: none;padding: 8px;cursor: pointer;" onclick="Redirect(\''+'cat'+'*'+str(i)+'\')">'+title_mapper[x][lang]+'</b>' if category==x else '<p style="display: inline;text-decoration: none;padding: 8px;cursor: pointer;" onclick="Redirect(\''+'cat'+'*'+str(i)+'\')">'+title_mapper[x][lang]+'</p>') for i,x in enumerate(category_list)])+'</h1>'+\
                    '<select onchange="Redirect(\'lang*\'+this.value)"><option value="0" '+('selected="selected"' if 0 in s.get('lang',{}) else '')+'>日本語</option><option value="1" '+('selected="selected"' if 1 in s.get('lang',{}) else '')+'>繁體中文</option><option value="2" '+('selected="selected"' if 2 in s.get('lang',{}) else '')+'>简体中文</option><option value="3" '+('selected="selected"' if 3 in s.get('lang',{}) else '')+'>English</option></select>'+\
                    '<div style="margin-top:16px">')+\
                    ''.join([
                            '<div style="margin-top:8px"><span style="display:inline-block; width: 50px;" class="w3-margin-right">'+key_mapper[category][lang][x]+'</span>'+\
                                ''.join([('<button class="w3-button w3-black" onclick="Redirect(\''+x+'-'+str(i)+'\')">'+value_mapper[category][lang][x][i]+'</button>' if i in s.get(x,{}) else '<button class="w3-button w3-white" onclick="Redirect(\''+x+'+'+str(i)+'\')">'+value_mapper[category][lang][x][i]+'</button>') for i in range(len(value_mapper[category][lang][x]))])+'</div>'
                        for x in header_order[category]])+\
                    ('</div><div style="margin-top:8px;margin-bottom:16px" class="w3-bottombar"><span style="display:inline-block; width: 50px;" class="w3-margin-right">'+key_mapper[category][lang]['order']+'</span>')+\
                    ''.join([('<button class="w3-button w3-black" onclick="Redirect(\'order*'+str(i)+'\')">'+value_mapper[category][lang]['order'][i]+'</button>' if i in s.get('order',{}) else '<button class="w3-button w3-white" onclick="Redirect(\'order*'+str(i)+'\')">'+value_mapper[category][lang]['order'][i]+'</button>') for i in range(len(value_mapper[category][lang]['order']))])+\
                    ('</div></header><!-- First Photo Grid--><div id="chara_panel" class="w3-row-padding" style="display: flex;flex-wrap: wrap;">')+\
                    (''.join([
                        ('<div class="w3-third w3-container" style="width:440px;margin: 0 auto;margin-bottom:16px">'+\
                        (('<a href=\"https://honey2-img.s3-ap-northeast-1.amazonaws.com/'+category+'/image/honey2_'+category+'_'+x['id']+'.png'+'\">') if mode==1 else '')+\
                        '<img src="https://honey2-img.s3-ap-northeast-1.amazonaws.com/'+category+'/thumb'+('_pc/s_p_honey2_' if category=='chara' else '/s_honey2_')+category+'_'+x['id']+'.jpg'+'" alt="'+x['id']+'" style='+header_style[category][0]+' class="w3-hover-opacity"'+((' onclick="download_data(\'honey2_'+category+'_'+x['id']+'.png\')"') if mode==0 else '')+'>'+('</a>' if mode==1 else '')+\
                        '<div class="w3-white" style='+header_style[category][1]+'><p><b>'+x['name']+'</b><br><em style="cursor:pointer;" onclick="Redirect(\'uploader_uuid*'+str(x['uploader_uuid'])+'\')">'+user_dict[x['uploader_uuid']]+'</em></p><p>'+x['comment']+\
                        ''.join([('<p style="line-height: 10px;"><b>'+key_mapper[category][lang][h]+': '+(value_mapper[category][lang][h][x[h]] if x[h]<len(value_mapper[category][lang][h]) else '')+'</b></p>') for h in header_order[category]])+\
                        '</div></div>')
                        for x in r_list]))+\
                    ('</div><!-- Pagination --><div class="w3-center w3-padding-32"><div class="w3-bar">')+\
                    ('<button class="w3-bar-item w3-button w3-hover-black" onclick="Redirect(\'page*1\')">««</button>')+\
                    ('<button class="w3-bar-item w3-button w3-hover-black" onclick="Redirect(\'page-1\')">«</button>')+\
                    ('' if (page-2)<1 else '<button class="w3-bar-item w3-button w3-hover-black" onclick="Redirect(\'page-2\')">'+str(page-2)+'</button>')+\
                    ('' if (page-1)<1 else '<button class="w3-bar-item w3-button w3-hover-black" onclick="Redirect(\'page-1\')">'+str(page-1)+'</button>')+\
                    ('<button class="w3-bar-item w3-black w3-button">'+str(page)+'</button>')+\
                    ('' if (page+1)>max_page else '<button class="w3-bar-item w3-button w3-hover-black" onclick="Redirect(\'page+1\')">'+str(page+1)+'</button>')+\
                    ('' if (page+2)>max_page else  '<button class="w3-bar-item w3-button w3-hover-black" onclick="Redirect(\'page+2\')">'+str(page+2)+'</button>')+\
                    ('<button class="w3-bar-item w3-button w3-hover-black" onclick="Redirect(\'page+1\')">»</button>')+\
                    ('<button class="w3-bar-item w3-button w3-hover-black" onclick="Redirect(\'page*'+str(max_page)+'\')">»»</button>')+\
                    ('</div></div><!-- End page content --></div></body></html>')
                self.wfile.write(bytes(s,'utf-8'))
            except:
                traceback.print_exc()
#                from IPython import embed
#                embed()
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=UTF-8')
                self.end_headers()
                self.connection.shutdown(1)
        return
    def do_POST(self):
        print(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
        self.send_response(200, 'ok')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

#def check_client_quota(ip):
#    global hourly_client_quota
#    global daily_client_quota
#    global client_quota_hour_time
#    global ban_list
#    
#    #check hourly quota
#    current_hour_time=time.time()//3600
#    if(client_quota_hour_time!=current_hour_time):
#        hourly_client_quota=dict()
#        client_quota_hour_time=current_hour_time
#    
#    flag=True
#    if(ip in hourly_client_quota):
#        hourly_client_quota[ip]+=1
#        if(hourly_client_quota[ip]>max_hourly_client_quota):
#            flag=False
#    else:
#        hourly_client_quota[ip]=1
#
#    #check daily quota
#    if(ip in daily_client_quota):
#        daily_client_quota[ip]+=1
#        if(daily_client_quota[ip]>max_daily_client_quota):
#            flag=False
#    else:
#        daily_client_quota[ip]=1
#    if(not flag):
#        ban_list.append(ip)
#    return flag

#def add_file_valid(ip,id_list):
#    global valid_ip_file_dict
#    if(ip not in valid_ip_file_dict):
#        valid_ip_file_dict[ip]=set()
#    valid_ip_file_dict[ip].update(id_list)

#def check_file_valid(ip,id):
#    global valid_ip_file_dict
#    if(ip in valid_ip_file_dict and id in valid_ip_file_dict[ip]):
#        return True
#    else:
#        if(check_client_quota(ip)):
#            return True
#        else:
#            return False

def parse_scene(mode='full'):
    if(mode=='full'):
        pass
        update_url='http://uphs2.illusion.jp/list_scene.php?&order_by=createtime%2Cdesc&page='
        dl_url='http://uphs2.illusion.jp/list_scene.php?&order_by=dlcount%2Cdesc&page='
        wdl_url='http://uphs2.illusion.jp/list_scene.php?&order_by=weekcount%2Cdesc&page='
        scene_list=list()
        missing_val_iter=iter(range(-1,int(-1e6),-1))
        reverse_user_dict=dict()
        negative_val_iter=iter(range(-1,int(-1e6),-1))
        id_index_mapper=dict()
        #get update_url and create template list
        counter=0
        while(True):
            counter+=1
            next_url=update_url+str(counter)
            print(next_url)
            page=requests.get(next_url,cookies={'limit':'100'}).content
            tree=html.fromstring(page)
            id_list=['{:07d}'.format(int(x.replace('img',''))) for x in tree.xpath('//div[@class="picture"]/@id')]
            uploader_uuid_list=[reverse_user_dict.setdefault(x.replace('\\n','').replace('by ','').strip(),next(missing_val_iter)) for x in tree.xpath('//div[@class="col-xs-7 handle_name text-right scene_handle_name"]/a/div/text()')]
            name_list=[x.replace('\\n','').replace('by ','').strip() for x in tree.xpath('//div[@class="caption"]/h3/text()')]
            comment_list=[x.replace('\\n','').replace('by ','').strip() for x in tree.xpath('//div[@class="pricebox comment"]/div/div/text()')]
            update_list=[next(negative_val_iter) for x in range(len(id_list))]
            new=False#flag
            for id,uploader_uuid,name,comment,update in zip(id_list,uploader_uuid_list,name_list,comment_list,update_list):
                if(id not in id_index_mapper):
                    new=True
                    id_index_mapper[id]=len(scene_list)
                    scene_list.append({
                        'id':id,'uploader_uuid':uploader_uuid,'name':name,'comment':comment,'update':update
                    })
            if(not new):
                break
        counter=0
        #dl
        counter=0
        negative_val_iter=iter(range(-1,int(-1e6),-1))
        while(True):
            counter+=1
            next_url=dl_url+str(counter)
            print(next_url)
            page=requests.get(next_url,cookies={'limit':'100'}).content
            tree=html.fromstring(page)
            id_list=['{:07d}'.format(int(x.replace('img',''))) for x in tree.xpath('//div[@class="picture"]/@id')]
            dl_list=[next(negative_val_iter) for x in range(len(id_list))]
            new=False#flag
            for id,dl in zip(id_list,dl_list):
                #check write
                if(id not in id_index_mapper):
                    continue
                if('dl' not in scene_list[id_index_mapper[id]]):
                    new=True
                    scene_list[id_index_mapper[id]]['dl']=dl
            if(not new):
                break
        #wdl
        counter=0
        negative_val_iter=iter(range(-1,int(-1e6),-1))
        while(True):
            counter+=1
            next_url=wdl_url+str(counter)
            print(next_url)
            page=requests.get(next_url,cookies={'limit':'100'}).content
            tree=html.fromstring(page)
            id_list=['{:07d}'.format(int(x.replace('img',''))) for x in tree.xpath('//div[@class="picture"]/@id')]
            wdl_list=[next(negative_val_iter) for x in range(len(id_list))]
            new=False#flag
            for id,wdl in zip(id_list,wdl_list):
                #check write
                if(id not in id_index_mapper):
                    continue
                if('wdl' not in scene_list[id_index_mapper[id]]):
                    new=True
                    scene_list[id_index_mapper[id]]['wdl']=wdl
            if(not new):
                break
    elif(mode=='acc'):
        pass
    return (scene_list,reverse_user_dict)

def StartServer():
    sever = ThreadingHTTPServer(("",int(os.environ.get('PORT',40005))),PostHandler)
    #sever = HTTPServer(("",9999),PostHandler)
    #sever.socket = ssl.wrap_socket (sever.socket, certfile='server.pem', server_side=True)
    print('ready')
    sever.serve_forever()

if __name__=='__main__':
    #
    print('port='+str(os.environ.get('PORT',40005)))
    proxy=json.load(open('proxy.json','r'))
    proxy={proxy['protocol']:proxy['ip']+':'+proxy['port']}
    #parse uploader data
    sess=requests.Session()
    a=sess.post('http://uphs2.illusion.jp/interface/user.php',data={'mode':'2'})
    user_dict=dict()#will be create after scene data download
    reverse_user_dict=dict()
    with open('user_status.txt','w',encoding='utf-8') as f:
        for line in a.text.split('\n'):
            uid,uname=[base64.b64decode(x).decode('utf-8') for x in line.split('\t')]
            user_dict[int(uid)]=uname
            reverse_user_dict[uname]=int(uid)
    #parse uploader data end
    #download chara data
    sess=requests.Session()
    a=sess.post('http://uphs2.illusion.jp/interface/chara.php',data={'mode':'0'})
    full_list=list()
    with open('chara_status.txt','w',encoding='utf-8') as f:
        for line in a.text.split('\n'):
            chara_id,guid,uploader_uuid,chara_name,characteristics,birth_month,birth_day,comment,sex,height,breast,hair_style,feature,mood,h_attributes,total_download,weekly_download,likes,update_time,version,create_time=[base64.b64decode(x).decode('utf-8') for x in line.split('\t')]
            if(create_time=='0000-00-00 00:00:00' or update_time=='0000-00-00 00:00:00'):
                continue
            tmp={'chara_id':chara_id,'guid':guid,'uploader_uuid':uploader_uuid,'chara_name':chara_name,'characteristics':characteristics,
            'birth_month':birth_month,'birth_day':birth_day,'comment':comment,
            'sex':sex,'height':height,'breast':breast,'hair_style':hair_style,
            'feature':feature,'mood':mood,'h_attributes':h_attributes,
            'total_download':total_download,'weekly_download':weekly_download,'likes':likes,
            'update_time':update_time,'version':version,'create_time':create_time}
            full_list.append(tmp)
        f.write('[\n')
        for d in full_list[:-1]:
            f.write('    '+json.dumps(d,ensure_ascii=False)+',\n')
        else:
            f.write('    '+json.dumps(full_list[-1],ensure_ascii=False)+'\n')
        f.write(']')
    with open('chara_status.txt','r',encoding='utf-8') as f:
        original_list=json.loads(f.read())
    chara_list=[{'id':'{:07d}'.format(int(x['chara_id'])),
        'uploader_uuid':int(x['uploader_uuid']),
        'name':x['chara_name'],
        'type':int(x['characteristics']),
        'comment':x['comment'],
        'sex':int(x['sex']),
        'height':int(x['height']),
        'breast':int(x['breast']),
        'hair':int(x['hair_style']),
        'update':int(time.mktime(datetime.datetime.strptime(x['update_time'], "%Y-%m-%d %H:%M:%S").timetuple())),
        'create':int(time.mktime(datetime.datetime.strptime(x['create_time'], "%Y-%m-%d %H:%M:%S").timetuple())),
        'dl':int(x['total_download']),
        'wdl':int(x['weekly_download']),
        'like':int(x['likes'])
        } for x in original_list]
    del full_list
    del original_list
    chara_list_update=sorted(chara_list,key=lambda x:x['update'],reverse=True)
    chara_list_create=sorted(chara_list,key=lambda x:x['create'],reverse=True)
    chara_list_dl=sorted(chara_list,key=lambda x:x['dl'],reverse=True)
    chara_list_wdl=sorted(chara_list,key=lambda x:x['wdl'],reverse=True)
    chara_list_like=sorted(chara_list,key=lambda x:x['like'],reverse=True)
    del chara_list
    #download chara data end
    #[new]download scene data
    scene_list,reverse_user_dict=parse_scene()
    scene_list_update=sorted(scene_list,key=lambda x:x['update'],reverse=True)
    scene_list_create=scene_list_update
    scene_list_dl=sorted(scene_list,key=lambda x:x['dl'],reverse=True)
    scene_list_wdl=sorted(scene_list,key=lambda x:x['wdl'],reverse=True)
    scene_list_like=scene_list_dl
    del scene_list
    #[new]download scene data end
    #[new]append user_dict
    user_dict.update(dict([(k,v) for v,k in reverse_user_dict.items() if k<0]))
    #[new]append user_dict end
    
#    #download scene data
#    sess=requests.Session()
#    a=sess.post('http://upai.illusion.jp/interface/scene.php',data={'mode':'0'})
#    full_list=list()
#    missing_val_iter=iter(range(-1,int(-1e6),-1))
#    with open('scene_status.txt','w',encoding='utf-8') as f:
#        for line in a.text.split('\n'):
#            scene_id,guid,uploader_uuid,scene_name,uploader_name,comment,total_download,weekly_download,likes,update_time,version=[base64.b64decode(x).decode('utf-8') for x in line.split('\t')]
#            tmp={'scene_id':scene_id,'guid':guid,'uploader_uuid':uploader_uuid,'scene_name':scene_name,'uploader_name':uploader_name,
#            'comment':comment,'total_download':total_download,'weekly_download':weekly_download,'likes':likes,
#            'update_time':update_time,'version':version}
#            full_list.append(tmp)
#        f.write('[\n')
#        for d in full_list[:-1]:
#            f.write('    '+json.dumps(d,ensure_ascii=False)+',\n')
#        else:
#            f.write('    '+json.dumps(full_list[-1],ensure_ascii=False)+'\n')
#        f.write(']')
#    with open('scene_status.txt','r',encoding='utf-8') as f:
#        original_list=json.loads(f.read())
#    scene_list=[{'id':'{:07d}'.format(int(x['scene_id'])),
#        'uploader_uuid':reverse_user_dict.setdefault(x['uploader_name'],next(missing_val_iter)),
#        'name':x['scene_name'],
#        'comment':x['comment'],
#        'update':int(time.mktime(datetime.datetime.strptime(x['update_time'], "%Y-%m-%d %H:%M:%S").timetuple())),
#        'dl':int(x['total_download']),
#        'wdl':int(x['weekly_download']),
#        'like':int(x['likes'])
#        } for x in original_list]
#    del full_list
#    del original_list
#    scene_list_update=sorted(scene_list,key=lambda x:x['update'],reverse=True)
#    scene_list_create=scene_list_update
#    scene_list_dl=sorted(scene_list,key=lambda x:x['dl'],reverse=True)
#    scene_list_wdl=sorted(scene_list,key=lambda x:x['wdl'],reverse=True)
#    scene_list_like=sorted(scene_list,key=lambda x:x['like'],reverse=True)
#    del scene_list
#    #download scene data end
#    #append user_dict
#    user_dict.update(dict([(k,v) for v,k in reverse_user_dict.items() if k<0]))
#    #append user_dict end
#    #download housing data
#    sess=requests.Session()
#    a=sess.post('http://upai.illusion.jp/interface/housing.php',data={'mode':'0'})
#    full_list=list()
#    with open('housing_status.txt','w',encoding='utf-8') as f:
#        for line in a.text.split('\n'):
#            housing_id,guid,uploader_uuid,housing_name,housing_type,comment,total_download,weekly_download,likes,update_time,version,create_time=[base64.b64decode(x).decode('utf-8') for x in line.split('\t')]
#            
#            tmp={'housing_id':housing_id,'guid':guid,'uploader_uuid':uploader_uuid,'housing_name':housing_name,'housing_type':housing_type,
#            'comment':comment,'total_download':total_download,'weekly_download':weekly_download,'likes':likes,
#            'update_time':update_time,'version':version,'create_time':create_time}
#            full_list.append(tmp)
#        f.write('[\n')
#        for d in full_list[:-1]:
#            f.write('    '+json.dumps(d,ensure_ascii=False)+',\n')
#        else:
#            f.write('    '+json.dumps(full_list[-1],ensure_ascii=False)+'\n')
#        f.write(']')
#    with open('housing_status.txt','r',encoding='utf-8') as f:
#        original_list=json.loads(f.read())
#    housing_list=[{'id':'{:07d}'.format(int(x['housing_id'])),
#        'uploader_uuid':int(x['uploader_uuid']),
#        'name':x['housing_name'],
#        'size':int(x['housing_type']),
#        'comment':x['comment'],
#        'update':int(time.mktime(datetime.datetime.strptime(x['update_time'], "%Y-%m-%d %H:%M:%S").timetuple())),
#        'create':int(time.mktime(datetime.datetime.strptime(x['create_time'], "%Y-%m-%d %H:%M:%S").timetuple())),
#        'dl':int(x['total_download']),
#        'wdl':int(x['weekly_download']),
#        'like':int(x['likes'])
#        } for x in original_list]
#    del full_list
#    del original_list
#    housing_list_update=sorted(housing_list,key=lambda x:x['update'],reverse=True)
#    housing_list_create=sorted(housing_list,key=lambda x:x['create'],reverse=True)
#    housing_list_dl=sorted(housing_list,key=lambda x:x['dl'],reverse=True)
#    housing_list_wdl=sorted(housing_list,key=lambda x:x['wdl'],reverse=True)
#    housing_list_like=sorted(housing_list,key=lambda x:x['like'],reverse=True)
#    del housing_list
#    #download housing data end
    data_list={'chara':[chara_list_update,chara_list_create,chara_list_dl,chara_list_wdl,chara_list_like],
            'scene':[scene_list_update,scene_list_create,scene_list_dl,scene_list_wdl,scene_list_like]}#,
#            'housing':[housing_list_update,housing_list_create,housing_list_dl,housing_list_wdl,housing_list_like]}
    system_boot_time=datetime.datetime.now()
    scheduled_reboot_time=system_boot_time.replace(hour=0, minute=0, second=0, microsecond=0)+datetime.timedelta(days=1)
    reboot_interval=(scheduled_reboot_time-system_boot_time).total_seconds()
    reboot_timer=Timer(reboot_interval, os._exit, args=[0])
    reboot_timer.start()
    #
    StartServer()
