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

from fengmian.models import MyUser
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
        if xuliehaos == self.give_over or today_received_nums >= 30:
            return render(request,'fengmian/index.html',context)
       
        xuliehao = xuliehaos.split('\n').pop(0)
        if current_user:
            current_time = datetime.datetime.now()
            access_time = current_user[0].access_time
            if current_time > access_time + datetime.timedelta(hours=8):
                # update user database
                MyUser.objects.filter(ip=ip).update(xuliehao=xuliehao)
            else:
                xuliehao = f'时间间隔太短了哦 上次提取时间:\n {access_time.strftime("%Y-%m-%d %H:%M:%S")}'
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
            # new_data = set(data) - set(false_data)
            # new_data_str = '\n'.join(list(new_data))
            # self._update_xuliehao(new_data_str)
        # MyUser.objects.all().delete() 