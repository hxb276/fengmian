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

import requests

from fengmian.models import MyUser,AdCity
from fengmian.utils import get_ip
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
        ip = get_ip(request)
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

class AdCityView(View):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.day = datetime.datetime.now().strftime('%d')

    def get(self,request):
        ''''''
        ip = get_ip(request)
        
        today_ip = AdCity.objects.filter(ip=ip,access_time__day=self.day)
        if not today_ip:
            AdCity.objects.create(ip=ip)

        all_visitors = AdCity.objects.all()
        visitors = all_visitors.count()
        current_visitors = all_visitors.filter(access_time__day=self.day).count()
        wd_visitors, today_pay = self.get_wd_visitors()
        city2wdper = int(wd_visitors) / int(current_visitors)
        
        context = {
            'vs':visitors,
            'cvs':current_visitors,
            'wcvs':wd_visitors,
            'tpay':today_pay,
            'city2wdper': round(city2wdper,2)
            }
        return render(request,'fengmian/adcity.html',context)


    def get_wd_visitors(self):
        url = 'https://thor.weidian.com/didataserver/reporthome.queryPcHomeCoreData/1.0'
        headers = {
            'user-agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'Referer':'https://d.weidian.com/',
            'cookie':'__spider__visitorid=038fc2533bb59653; visitor_id=3199c277-7521-41f7-86b1-e57c315bf9c2; vc_fpcookie=6178ca1b-8b91-74d1-34d9-9e182fa841cb; is_login=true; login_type=LOGIN_USER_TYPE_MASTER; login_source=LOGIN_USER_SOURCE_MASTER; uid=1164129036; duid=1164129036; sid=1164129036; WD_wfr=c; wdtoken=3baecaca; __spider__sessionid=2364e40913b29b56; v-components/clean-up-advert@private_domain=1164129036; v-components/clean-up-advert@wx_app=1164129036; Hm_lvt_f3b91484e26c0d850ada494bff4b469b=1642402537,1642922850,1642957826; Hm_lpvt_f3b91484e26c0d850ada494bff4b469b=1642957826; login_token=MlKFrL9BkJSZt7O8QI9AaZs1Una3BC8HrAsaWOBA8qk8ZysaLL6WEEmZzNmwH2RxzMDPbRwIXr1J9dkOxrxgTaQurLO-rLmgQAQN4SbTQD81vvujJj2FXlgxZxE8ZGsPqRwVliclkonWYNQXImYCV2xgsUYw15tmOuFP08a5g4rXGNU',
        }

        params = {
            'wdtoken':'3baecaca',
            '_':str(time.time()*1000).split('.')[0]
        }
        res = requests.get(url,headers=headers,params=params)
        data = res.json()
        if 'status' in data and data['status']['message'] == 'OK':
            result = data['result']
            today = result['today']
            today_vistors = today[-1]['num']
            today_pay_nums = today[0]['num']

            return today_vistors,today_pay_nums
        else:
            return 0,0


if __name__ == '__main__':
    ad = AdCityView()
    t =ad.get_wd_visitors()
    print(t)