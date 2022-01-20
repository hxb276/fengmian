'''
@version 0.1.2
@author hua
@email xxx.com
'''
from pathlib import Path
import json
import time
import datetime
from hashlib import md5

from django.shortcuts import render
from django.views.generic import View

from .models import MyUser
# Create your views here.

class IndexView(View):
    '''
    base view
    '''
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.give_over = '今天的赠送名额领完了,明天再来吧'
        self.day = datetime.datetime.now().strftime('%d')
        self.__create_false_data()

    def get(self,request):
        ip = self._get_ip(request)
        encrypted_ip = md5(ip.encode(encoding='utf8')).hexdigest()
        all_user = MyUser.objects.all().order_by('-access_time')
        all_received_nums = all_user.count()
        today_received_nums = MyUser.objects.filter(access_time__day=self.day).count()
        current_user = MyUser.objects.filter(ip=ip)
        show_10 = all_user[:10].values('xuliehao','access_time')

        xuliehaos = self._get_xuliehao() or self.give_over
        
        context = {
                'xuliehao':self.give_over,
                'ip':encrypted_ip,
                'show_10':show_10,
                'all_received_nums':all_received_nums
                }

        # 每天限量20个，领完不在返回序列号
        if xuliehaos == self.give_over or today_received_nums == 15:
            return render(request,'fengmian/index.html',context)
       
        xuliehao = xuliehaos.split('\n').pop(0)
        if current_user:
            current_time = datetime.datetime.now()
            access_time = current_user[0].access_time
            if current_time > access_time + datetime.timedelta(hours=8):
                print(xuliehao)
                # update user database
                MyUser.objects.filter(ip=ip).update(xuliehao=xuliehao)
            else:
                xuliehao = f'时间间隔太短了哦 上次提取时间:\n {access_time.strftime("%Y-%m-%d %H:%M:%S")}'
                print(MyUser.objects.all().values())
        else:
            MyUser.objects.create(ip=ip,xuliehao=xuliehao)
        
        # update xuliehao txt : delete already in used xuliehao
        xuliehaos = xuliehaos.replace(xuliehao+'\n','')
        self._update_xuliehao(xuliehaos)

        context['xuliehao'] = xuliehao
        return render(request,'fengmian/index.html',context)
    
    def _get_ip(self,request):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get("HTTP_X_FORWARDED_FOR")
        else:
            ip = request.META.get("REMOTE_ADDR")
        
        return ip

    def _get_xuliehao(self):
        with open('uploads/xuliehao.txt','r',encoding='utf8') as f:
            xuliehao = f.read()

        return xuliehao
    
    def _update_xuliehao(self,data):
        with open('uploads/xuliehao.txt','w',encoding='utf8') as f:
            f.write(data)

    def __create_false_data(self):
        '''
        false data
        '''
        count = MyUser.objects.all().count()
        data = self._get_xuliehao().split('\n')
        false_data = data[:20-count]
        if count < 20:
            false_ip = '127.0.0.'
            objects = [MyUser(ip=false_ip+str(i),xuliehao=data) for i,data in enumerate(false_data)]
            MyUser.objects.bulk_create(objects)
            # set 取差集
            new_data = set(data) - set(false_data)
            new_data_str = '\n'.join(list(new_data))
            self._update_xuliehao(new_data_str)
        # MyUser.objects.all().delete()




# def get_number(request):
#     '''
#     从数据库取数据，判断记录ip是否存，如果存在，时间是否超过14小时，如果不存在，则返回序列号
    
#     '''
#     give_over = '今天的赠送名额领完了,明天再来吧'
#     today = time.strftime('%m%d',time.localtime())
#     ip = get_ip(request)
#     encrypted_ip = md5(ip.encode(encoding='utf8')).hexdigest()
#     all_user = MyUser.objects.all().order_by('-access_time')
#     all_received_nums = all_user.count()
#     today_received_nums = MyUser.objects.filter(access_time=datetime.date.today()).count()
#     current_user = MyUser.objects.filter(ip=ip)
#     show_10 = all_user[:10].values('xuliehao','access_time')
#     data = get_record()
#     xuliehaos = get_xuliehao() or give_over

#     # 每天限量20个，领完不在返回序列号
#     if xuliehaos == give_over or today_received_nums == 20:
        
#         return render(request,'fengmian/index.html',{
#                 'xuliehao':xuliehaos,
#                 'ip':encrypted_ip,
#                 'presented':show_presented,
#                 'presented_total':presented_total
#                 })
    
#     current_time = datetime.datetime.now()
#     if data:
#         # 数据结构：{'127.':time}
#         if ip in data:
#             times = data[ip]
#             # ip相同，间隔时间超8小时
#             if time.time() - times < 2:
#                 print(times)
#                 xuliehao = f'时间间隔太短了哦 上次提取时间:\n {time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(times))}'
#             # 新老用户一视同仁
#             else:
#                 xuliehao = xuliehaos.split('\n').pop(0)
#                 data[ip] = time.time()
#                 update_userinfo(data)
#                 # 今天是否有领取记录，有则直接append 否则创建时间键today
#                 if presented.get(today,None):
#                     presented[today].append({'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')})
#                 else:
#                     presented[today] = [{'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')}]
#                 update_presented(presented)
        
#         else:
#             xuliehao = xuliehaos.split('\n').pop(0)
#             data.update({str(ip):time.time()})
#             update_userinfo(data)
#             # 今天是否有领取记录，有则直接append 否则创建时间键today
#             if presented.get(today,None):
#                 presented[today].append({'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')})
#             else:
#                 presented[today] = [{'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')}]
#             update_presented(presented)

#     else:
#         # 程序第一次执行 所有数据为空
#         data = dict()
#         xuliehao = xuliehaos.split('\n').pop(0)
#         data.update({str(ip):time.time()})
#         update_userinfo(data)
#         presented[today] = [{'name':xuliehao,'time':current_time.strftime('%Y-%m-%d %H:%M:%S')}]
#         update_presented(presented)

#     replace_str = xuliehao+'\n' 
#     if len(xuliehaos.split('\n')) > 1:
#         new_xuliehaos = xuliehaos.replace(replace_str,'')
#     else:
#         new_xuliehaos = ''
#     update_xuliehao(new_xuliehaos)

#     return render(request,'fengmian/index.html',{'xuliehao':xuliehao,'ip':encrypted_ip,'presented':show_presented,'presented_total':presented_total})

# def get_ip(request):
#     if request.META.get('HTTP_X_FORWARDED_FOR'):
#         ip = request.META.get("HTTP_X_FORWARDED_FOR")
#     else:
#         ip = request.META.get("REMOTE_ADDR")
#     return ip

# def get_xuliehao():
#     with open('uploads/xuliehao.txt','r',encoding='utf8') as f:
#         xuliehao = f.read()

#     return xuliehao

# def update_xuliehao(txt):
#     with open('uploads/xuliehao.txt','w',encoding='utf8') as f:
#         f.write(txt)

# def get_record(info=dict()):
#     path = Path(MEDIA_ROOT / 'userinfo.json')
#     if not path.is_file():
#         return info
#     else:
#         with open(path,'r',encoding='utf8') as f:
#             data = f.read()

#     return json.loads(data) if data else dict()

# def update_userinfo(info):
#     path = Path(MEDIA_ROOT / 'userinfo.json')

#     with open(path,'w',encoding='utf8') as f:
#         infos = json.dumps(info)
#         f.write(infos)

# def get_presented(today):
#     '''
#     :today: 日期字符串
#     '''
#     default_values = dict({today:[]})
#     path = Path(MEDIA_ROOT / 'presented.json')
#     if not path.is_file():
#         with open(path,'w',encoding='utf8') as f:
#             f.write(json.dumps(default_values))
#         return default_values
#     with open(path,'r',encoding='utf8') as f:
#         data = f.read()
#         if data:
#             data = json.loads(data)
#         else:
#             data = default_values
#     return data
# def update_presented(data:dict()):
#     path = Path(MEDIA_ROOT / 'presented.json')
#     with open(path,'w',encoding='utf8') as f:
#         f.write(json.dumps(data))