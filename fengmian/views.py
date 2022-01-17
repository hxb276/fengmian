from marshal import loads
from pathlib import Path
import json
import time
import datetime
from hashlib import md5

from django.shortcuts import render

from fengmianapi.settings import MEDIA_ROOT

from .models import Xuliehao
# Create your views here.
def get_number(request):
    '''
    从数据库取数据，判断记录ip是否存，如果存在，时间是否超过14小时，如果不存在，则返回序列号
    
    '''
    give_over = '今天的赠送名额领完了'
    ip = md5(get_ip(request).encode(encoding='utf8')).hexdigest()
    data = get_record()
    xuliehaos = get_xuliehao() or give_over
    presented = get_presented()
    show_presented = presented[::-1][:10]
    presented_total = len(presented) if len(presented) < 9 else len(presented) + 40
    current_time = datetime.datetime.now()
    if data:
        for i,item in enumerate(data):
            old_ip = item['ip']
            times = item['time']
            # ip相同，间隔时间超8小时
            if ip == old_ip and time.time() - times < 2:
                xuliehao = f'时间间隔太短了哦 上次提取时间:\n {time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(times))}'
            elif ip == old_ip:
                xuliehao = xuliehaos.split(',').pop(0)
                data[i].update({'time':time.time()})
                update_userinfo(data)
                if xuliehao != give_over:
                    presented.append({'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')})
                    update_presented(presented)
            else:
                xuliehao = xuliehaos.split(',').pop(0)
                data.append({'ip':ip,'time':time.time()})
                update_userinfo(data)
                if xuliehao != give_over:
                    presented.append({'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')})
                    update_presented(presented)
    else:
        data = []
        xuliehao = xuliehaos.split(',').pop(0)
        data.append({'ip':ip,'time':time.time()})
        update_userinfo(data)
        if xuliehao != give_over:
            presented.append({'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')})
            update_presented(presented)

    replace_str = xuliehao+',' 
    if len(xuliehaos.split(',')) > 1:
        new_xuliehaos = xuliehaos.replace(replace_str,'')
    else:
        new_xuliehaos = ''
    update_xuliehao(new_xuliehaos)

    return render(request,'fengmian/index.html',{'xuliehao':xuliehao,'ip':ip,'presented':show_presented,'presented_total':presented_total})

def get_ip(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def get_xuliehao():
    with open('uploads/xuliehao.txt','r',encoding='utf8') as f:
        xuliehao = f.read()

    return xuliehao

def update_xuliehao(txt):
    print(txt)
    with open('uploads/xuliehao.txt','w',encoding='utf8') as f:
        f.write(txt)

def get_record(info=[]):
    path = Path(MEDIA_ROOT / 'userinfo.json')
    if not path.is_file():
        return info
    else:
        with open(path,'r',encoding='utf8') as f:
            data = f.read()

    return json.loads(data) if data else info

def update_userinfo(info):
    path = Path(MEDIA_ROOT / 'userinfo.json')

    with open(path,'w',encoding='utf8') as f:
        infos = json.dumps(info)
        f.write(infos)

def get_presented():
    path = Path(MEDIA_ROOT / 'presented.json')
    if not path.is_file():
        with open(path,'w',encoding='utf8') as f:
            f.write('')
        return []
    with open(path,'r',encoding='utf8') as f:
        data = f.read()
        data = json.loads(data) if data else []
    return data
def update_presented(data:list()):
    path = Path(MEDIA_ROOT / 'presented.json')
    with open(path,'w',encoding='utf8') as f:
        f.write(json.dumps(data))