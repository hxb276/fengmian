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
    give_over = '今天的赠送名额领完了,明天再来吧'
    today = time.strftime('%m%d',time.localtime())
    ip = get_ip(request)
    encrypted_ip = md5(ip.encode(encoding='utf8')).hexdigest()
    data = get_record()
    xuliehaos = get_xuliehao() or give_over
    presented = get_presented(today)
    all_presented =  []
    for item in list(presented.values()):
        all_presented += item
    show_presented = all_presented[::-1][:10]
    # 已领取总数量 
    presented_total = len(all_presented) if len(all_presented) < 10 else len(all_presented) + 40
    # 每天限量9个，领完不在返回序列号
    if not presented or xuliehaos == give_over or presented.get(today,None) and len(presented[today]) == 20:
        xuliehao = give_over
        return render(request,'fengmian/index.html',{
                'xuliehao':xuliehao,
                'ip':encrypted_ip,
                'presented':show_presented,
                'presented_total':presented_total
                })
    
    current_time = datetime.datetime.now()
    if data:
        # 数据结构：{'127.':time}
        if ip in data:
            times = data[ip]
            # ip相同，间隔时间超8小时
            if data[ip] - times < 28800:
                xuliehao = f'时间间隔太短了哦 上次提取时间:\n {time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(times))}'
            # 新老用户一视同仁
            else:
                xuliehao = xuliehaos.split('\n').pop(0)
                data[ip] = time.time()
                update_userinfo(data)
                # 今天是否有领取记录，有则直接append 否则创建时间键today
                if presented.get(today,None):
                    presented[today].append({'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')})
                else:
                    presented[today] = [{'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')}]
                update_presented(presented)

    else:
        # 程序第一次执行 所有数据为空
        data = dict()
        xuliehao = xuliehaos.split('\n').pop(0)
        data.update({str(ip):time.time()})
        update_userinfo(data)
        presented[today] = [{'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')}]
        update_presented(presented)

    replace_str = xuliehao+'\n' 
    if len(xuliehaos.split('\n')) > 1:
        new_xuliehaos = xuliehaos.replace(replace_str,'')
    else:
        new_xuliehaos = ''
    update_xuliehao(new_xuliehaos)

    return render(request,'fengmian/index.html',{'xuliehao':xuliehao,'ip':encrypted_ip,'presented':show_presented,'presented_total':presented_total})

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
    with open('uploads/xuliehao.txt','w',encoding='utf8') as f:
        f.write(txt)

def get_record(info=dict()):
    path = Path(MEDIA_ROOT / 'userinfo.json')
    if not path.is_file():
        return info
    else:
        with open(path,'r',encoding='utf8') as f:
            data = f.read()

    return json.loads(data) if data else dict()

def update_userinfo(info):
    path = Path(MEDIA_ROOT / 'userinfo.json')

    with open(path,'w',encoding='utf8') as f:
        infos = json.dumps(info)
        f.write(infos)

def get_presented(today):
    '''
    :today: 日期字符串
    '''
    default_values = dict({today:[]})
    path = Path(MEDIA_ROOT / 'presented.json')
    if not path.is_file():
        with open(path,'w',encoding='utf8') as f:
            f.write(json.dumps(default_values))
        return default_values
    with open(path,'r',encoding='utf8') as f:
        data = f.read()
        if data:
            data = json.loads(data)
        else:
            data = default_values
    return data
def update_presented(data:dict()):
    path = Path(MEDIA_ROOT / 'presented.json')
    with open(path,'w',encoding='utf8') as f:
        f.write(json.dumps(data))