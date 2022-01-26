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
import re
from tkinter import S
import urllib

from django.conf import settings
from django.http import (HttpResponse,
                        HttpResponseRedirect,
                        JsonResponse,
                        HttpResponseForbidden,
                        FileResponse)
from django.shortcuts import render
from django.views.generic import View

import requests

from fengmian.models import MyUser,AdCity
from fengmian.utils import get_ip,get_ua
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
        print(request.headers)
        
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
        # return render(request,'fengmian/adcity.html',context)
        return HttpResponseRedirect('http://fm666.hsenzy.com/')


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

class PddVideoview(View):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def get(self,request):
        
        if request.headers.get('Content-Type',None) == 'application/json':
            url = request.GET.get('ou',None)
            qq_number = request.GET.get('qid',None)

            if url:
                url_ok = self.__verity_url(url)
                if not url_ok:
                    return JsonResponse({'code':-1,'msg':'params err'})
                video_info = self.__get_video_url(url)
                return JsonResponse(video_info,safe=False)
            # 第一次验证qq号
            elif qq_number:
                ua = get_ua(request)
                res = JsonResponse({'code':1,'msg':'success'})
                res.set_signed_cookie('uid',str(qq_number),salt='ddsp')
                res.set_signed_cookie('ua',ua,salt='ddsp')
                return res
            else:
                return HttpResponseForbidden()
        else:
            print(request.META.get('QUERY_STRING',None))
            ua = get_ua(request)
            print(ua)
            return render(request,'fengmian/pdd-video.html')


    def __get_video_url(self,url):
        headers = {
        'Host':'mobile.yangkeduo.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3185 MMWEBSDK/20211202 Mobile Safari/537.36 MMWEBID/9626 MicroMessenger/8.0.18.2060(0x28001251) Process/toolsmp WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'X-Requested-With': 'com.tencent.mm',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': ''
        }
        params = {
            'feed_id':'4265981489507747070',
            'share_mall_id':'144905218',
            'page_from':'602100',
            'shared_time':'1643023430003',
            'shared_sign':'ecdc802498800a94b733a3ade35a7ffe',
            'goods_id':'312710602079',
            'refer_share_id':'ce22a348bf864f599d9dcdf377f7cdf9',
            'refer_share_uid':'4221292552',
            'refer_share_uin':'OEOFS6VAD5SYUGPV26DJIS534M_GEXDA',
            'refer_share_channel':'message',
            'refer_share_form':'card'
        }
        # url = 'https://mobile.yangkeduo.com/proxy/api/api/hub/zb_promotions_scene/weak/list/get?pdduid=2608448966231 '
        # url = 'https://mobile.yangkeduo.com/fyxmkief.html?feed_id=4265981489507747070&share_mall_id=144905218&page_from=602100&shared_time=1643023430003&shared_sign=ecdc802498800a94b733a3ade35a7ffe&goods_id=312710602079&refer_share_id=ce22a348bf864f599d9dcdf377f7cdf9&refer_share_uid=4221292552&refer_share_uin=OEOFS6VAD5SYUGPV26DJIS534M_GEXDA&refer_share_channel=message&refer_share_form=card'
        res = requests.get(url=url,headers=headers,verify=False)
        data = res.text

        play_url = re.findall(r'play_url=(.*?)&',data)
        first_frame_url = re.findall(r'"firstFrameUrl":"(.*?jpeg)',data)[1]
        info = re.findall(r'<p .*?>(.*?)</p>',data)
        print(info)
        author = info[0]
        likes = info[1]
        comments = info[2]
        v_url = urllib.parse.unquote(play_url[0])
        img_url= first_frame_url.encode('utf8').decode('unicode-escape')

        return [author,likes,comments,v_url,img_url]

    def __verity_url(self,url):
        '''
        简单验证url是否合法
        '''
        return 'goods_id' in url.split('&')

class FormatXuliehao(View):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def get(self,request):

        if request.headers.get('Content-Type',None) == 'application/json':
            fstr = request.GET.get('s',None)
            txt = request.GET.get('txt',None)
            print(fstr,txt)
            if fstr:
                print(fstr)
                new_str = self.format_str(fstr)
                if new_str:
                    self.save_txt(new_str)
                    return JsonResponse({'code':1,'msg':'success','data':new_str})
                else:
                    return JsonResponse({'code':1,'msg':'success','data':'未知错误'})
            elif txt:
                print(txt)
                response = FileResponse(open('uploads/fengmian.txt','rb'))
                response['Content-Disposition'] = 'attachment; filename="xuliehao.txt"'
                return response
            else:
                return JsonResponse({'code':-1,'msg':'err'})

        return render(request,'fengmian/re.html')
    
    def format_str(self,s):
        '''格式化字符串'''
        new_str = ''
        str_lst = s.split('\n')
        for item in str_lst:
            if '：' in item:
                item = item.split('：')[1]
            elif ':' in item:
                item = item.split(':')[1]
            try:
                s = re.search(r'[A-z0-9]+',item)[0] + '\n'
            except:
                continue
            else:
                new_str += s
        return new_str

    def save_txt(self,s):
        
        with open('uploads/fengmian.txt','w',encoding='utf8') as f:
            f.write(s)

if __name__ == '__main__':
    ad = AdCityView()
    t =ad.get_wd_visitors()
    print(t)