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
import urllib

from django.conf import settings
from django.forms.models import model_to_dict
from django.http import (HttpResponse,
                        HttpResponseRedirect,
                        JsonResponse,
                        HttpResponseForbidden,
                        FileResponse)
from django.shortcuts import render
from django.views.generic import View

import requests

from fengmian.models import MyUser,AdCity,PddUser,PddVideo,AllowedRgisterUser
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
        self.salt = 'ddsp'

    def get(self,request):
        ip = get_ip(request)
        ua = get_ua(request)
        # ajax请求
        if request.headers.get('Content-Type',None) == 'application/json':
            url = request.GET.get('ou',None)
            uid = request.GET.get('qid',None)

            if url:
                cookie_uid = request.get_signed_cookie('uid',salt=self.salt)
                # 更新每日限定的下载次数
                self.__update_downtimes()
                return self.__ajax_url(url,cookie_uid)
            # 验证qq号
            elif uid:
                return self.__ajax_register(uid,ua,ip)
            else:
                return HttpResponseForbidden()
        # html请求
        else:
            login = False # 登录标志，默认未登录
            try:
                uid = request.get_signed_cookie('uid',salt=self.salt)
                cua = request.get_signed_cookie('ua',salt=self.salt)
            except:
                pass
            else:
                u_info = PddUser.objects.filter(uid=uid)
                # 判断当前登录设备是否是常用设备
                if u_info.exists() and (u_info[0].ua1 == cua or u_info[0].ua2 == cua):
                    login = True
                    down_times = u_info[0].down_times
                    data = PddVideo.objects.all().order_by('down_time')[:10]
                    return render(request,'fengmian/pdd-video.html',{'login':login,'uid':uid,'times':down_times,'data':data})
                
            return render(request,'fengmian/pdd-video.html',{'login':login})

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
        first_frame_url = re.findall(r'(http.*?jpeg)',data)[1]
        info = re.findall(r'<p .*?>(.*?)</p>',data)
        publish_time = re.findall(r'(\d+-\d+-\d+)',play_url[0])

        data = {
            'url':urllib.parse.unquote(play_url[0]),
            'feed_id':'',
            'goods_id':'',
            'likes':info[1],
            'comments':info[2],
            'publish_time':publish_time[0],
            'img_url':first_frame_url.encode('utf8').decode('unicode-escape')
        }

        return data

    def __verity_url(self,url):
        '''
        简单验证url是否合法
        '''
        status = False
        if 'feed_id' in url and 'goods_id' in url:
            feed_id = re.findall(r'feed_id=(.*?)&',url)[0]
            goods_id = re.findall(r'goods_id=(\d+)',url)[0]
            status = True # 合法
        
        return feed_id,goods_id,status

    def __ajax_url(self,url,cookie_uid):
        '''
        解析视频url，返回视频的详细信息
        '''

        feed_id,goods_id,url_ok = self.__verity_url(url)
        
        if not url_ok:
            return JsonResponse({'code':-1,'msg':'params err'})
       
        user_info = PddUser.objects.filter(uid=cookie_uid)
        down_times = user_info[0].down_times
        # 下载次数用完
        if down_times == 0:
            return JsonResponse({'code':-2,'msg':'down_times err'})
        
        local_feed = PddVideo.objects.filter(feed_id=feed_id)
        # 判断视频是否在数据库中存在，存在则直接返回
        if local_feed.exists():
            video_info = model_to_dict(local_feed[0])
            video_info.pop('feed_id')
            video_info.pop('id')
            return JsonResponse({'code':0,'msg':'success','data':video_info})
        else:
            video_info = self.__get_video_url(url)
            
            url,_,_,likes,comments,published,_ = list(video_info.values())
            published = datetime.datetime.strptime(published,'%Y-%m-%d')
            # 保存用户查询，用于展示和减少查询次数
            PddVideo.objects.create(url=url,feed_id=feed_id,
                                    goods_id=goods_id,likes=likes,
                                    comments=comments,publish_time=published)
            # 更新（减少）下载次数
            down_times = down_times - 1 if down_times > 0 else 0
            user_info.update(down_times=down_times)
            video_info.update({'goods_id':goods_id})
            video_info.pop('feed_id')
            
            return JsonResponse({'code':0,'msg':'success','data':video_info})

    def __ajax_register(self,uid,ua,ip):
        '''
        验证账号或者注册
        '''
        u_info = PddUser.objects.filter(uid=uid)
        u_allowed = AllowedRgisterUser.objects.filter(uid=uid)
        is_exists = u_info.exists()
        is_allowed = u_allowed.exists()
        data = {'code':1,'msg':'success'}

        res = JsonResponse(data)
        res.set_signed_cookie('uid',str(uid),salt=self.salt)
        res.set_signed_cookie('ua',ua,salt=self.salt)

        # 首次使用，直接注册
        if not is_exists and is_allowed:
            PddUser.objects.create(uid=uid,ip=ip,ua1=ua)
        # 已经注册，但是在新设备登录，更新新设备
        elif is_exists and not u_info[0].ua2 and u_info[0].ua1 != ua:
            u_info.update(ua2=ua)
        # cookie 过期或清除了缓存
        elif is_exists and (u_info[0].ua1 == ua or u_info[0].ua2 == ua):
            return res
        # 没有注册资格
        elif not is_allowed:
            data.update({'code':-1,'msg':'not allowed!'})
            return JsonResponse(data)
        else:
            data.update({'code':-2,'msg':'equipment error'})
            return JsonResponse(data)
        return res

    def __update_downtimes(self):
        '''
        更新每日下载限定次数
        '''
        today = datetime.datetime.now().strftime('%d')
        all_user = PddUser.objects.all()
        if all_user.exists() and all_user[0].update_time != today:
            all_user.update(down_times=5,update_time=today)

class AddUserView(View):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def get(self,request):
        if request.headers.get('Content-Type',None) == 'application/json':
            uid = request.GET.get('uid',None)
            handle_type = request.GET.get('type',None)
            del_user = request.GET.get('delnum',None)
            # 添加单个用户
            if uid and handle_type == 'add':
                AllowedRgisterUser.objects.create(uid=uid)
            # 批量添加用户名单
            elif uid == 'huahua' and handle_type == 'addall':
                objects = self.__get_qqs()
                AllowedRgisterUser.objects.bulk_create(objects)
            # 删除用户
            elif uid and handle_type == 'delete':
                AllowedRgisterUser.objects.filter(uid=del_user).delete()
            else:
                return JsonResponse({'code':-1,'msg':'error'})
            return JsonResponse({'code':1,'msg':'success'})
        context = {
            'usernums':PddUser.objects.all().count(),
            'videonums':PddVideo.objects.all().count(),
        }
        return render(request,'fengmian/add-pdd-user.html',context)

    def __get_qqs(self):
        with open('uploads/qq.json','r',encoding='utf8') as f:
            data = json.loads(f.read())
        qq_list = data['data']
        objects = [AllowedRgisterUser(uid=qq) for qq in qq_list]
        return objects

class FormatXuliehao(View):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def get(self,request):

        return render(request,'fengmian/re.html')

    def post(self,request):
        if request.headers.get('Content-Type',None) == 'application/json':
            fstr = request.POST.get('s',None)
            txt = request.POST.get('txt',None)
            if fstr:
                new_str = self.format_str(fstr)
                if new_str:
                    self.save_txt(new_str)
                    return JsonResponse({'code':1,'msg':'success','data':new_str})
                else:
                    return JsonResponse({'code':1,'msg':'success','data':'未知错误'})
            elif txt: 
                response = FileResponse(open('uploads/fengmian.txt','rb'))
                response['Content-Disposition'] = 'attachment; filename="xuliehao.txt"'
                return response
            else:
                return JsonResponse({'code':-1,'msg':'err'})

    
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