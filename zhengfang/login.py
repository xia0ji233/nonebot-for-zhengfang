import requests
import base64
import re
import sys
# import rsa
import six
import json
from bs4 import BeautifulSoup
from .RSAJS import *
from .hex2b64 import HB64
from time import time,localtime,strftime
import ssl

# 加密密码
def password(pw, modulus, exponent):
    exponent = HB64().b642hex(exponent)
    modulus = HB64().b642hex(modulus)
    rsa = RSAKey()
    rsa.setPublic(modulus, exponent)
    cry_data = rsa.encrypt(pw)
    return HB64().hex2b64(cry_data)


class session():
    def __init__(self, yhm, pw):
        self.yhm = yhm
        self.pw = pw
        # self.s为类的核心
        self.get_url = 'http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html'  # 登录链接
        self.post_url = 'http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html'  # 提交链接
        self.s = requests.Session()

    # 核心代码,登录
    def login(self):
        if True:
            head = {
                "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
                "Cache-Control": "max-age=0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
                "Content-Type": "application/x-www-form-urlencoded",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
                "Accept-Encoding": "gzip, deflate",
                "Host": "jwzx.zjxu.edu.cn",
                "Connection": "Keep-Alive"
            }
            # 获取登录页面
            r = self.s.get(url=self.get_url, headers=head)

            csrftoken = re.search('<input type="hidden" id="csrftoken" name="csrftoken" value="(.*?)"/>', r.text).group(1)

            head = {
                "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
                "X-Requested-With": "XMLHttpRequest",
                "Accept-Encoding": "gzip, deflate",
                "Host": "jwzx.zjxu.edu.cn",
                "Connection": "Keep-Alive",
                "Pragma": "no-cache",
            }

            # 获取公钥
            r = self.s.get('http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_getPublicKey.html', headers=head)

            modulus = r.json()['modulus']
            exponent = r.json()['exponent']

            enpassword = password(self.pw, modulus, exponent)

            # 要提交的表单
            data = {
                'csrftoken': csrftoken,
                'yhm': self.yhm,
                'mm': enpassword,
                'mm': enpassword
            }
            # 表单请求头
            head = {
                "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
                "Cache-Control": "max-age=0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
                "Content-Type": "application/x-www-form-urlencoded",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
                "Accept-Encoding": "gzip, deflate",
                "Host": "jwzx.zjxu.edu.cn",
                "Connection": "Keep-Alive",
            }
            # 提交表单
            r = self.s.post(self.post_url, data=data, headers=head)
            print(self.yhm)
            print(self.pw)
            ppot = r'用户名或密码不正确'
            if re.findall(ppot, r.text):
                print('用户名或密码错误,请查验..')
                return None
            else:
                print(r.headers)
                print(self.s.cookies.get_dict())
                print(r.history[0].cookies.get_dict())
                print(r.status_code)

                f = open('./src/plugins/zhengfang/1.log', 'w+')
                print(r.text, file=f)
                f.close()
                cookie = 'JSESSIONID=' + r.history[0].cookies.get_dict()['JSESSIONID']
                #cookie = r.request.headers['Cookie']
                print(cookie)
                print('登录成功\n')
                return cookie


    # 对外方法,进行重新登录
    def relogin(self):
        count = 0
        while 1:
            count += 1
            if self.login():
                return True
            if count > 10:
                # 如果多次失败则停止登录
                return False

    def get_info(self,cookie):
        url = 'http://jwzx.zjxu.edu.cn/jwglxt/xtgl/index_cxYhxxIndex.html'
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html?time=1598366187884",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        data = {
            'xt': 'jw',
            'localeKey': 'zh_CN',
            '_': str(time()),
            'gnmkdm': 'index',
            'su':self.yhm
        }
        p=self.s.get(url,headers=head,data=data,verify=False)
        bs = BeautifulSoup(p.text, "html.parser")
        # f=open('./src/plugins/zhengfang/1.log','w+')
        # print(p.text,file=f)
        # f.close()
        info={}
        info['name']=bs.h4.text
        cls=bs.p.text
        info['class']=cls[cls.find('学院 ')+3:]
        return info

    def term_judge(self, data):
        x = localtime(time())
        year = x.tm_year
        month = x.tm_mon
        if month < 2:
            data['xnm'] = str(year - 1)
            data['xqm'] = '3'
        elif month < 8:
            data['xnm'] = str(year - 1)
            data['xqm'] = '12'
        else:
            data['xnm'] = str(year)
            data['xqm'] = '3'
        return data



    def querypage(self,headers,params,data):
        url = 'http://jwzx.zjxu.edu.cn/jwglxt/cjcx/cjcx_cxDgXscj.html'
        res=self.s.post(url,data=data,headers=headers,params=params,verify=False)
        try:
            query_data=json.loads(res.text)['items']
        except:
            return None
        all_score=[]

        for item in query_data:
            s={}
            s['name'] = item['kcmc']
            s['score']=item['bfzcj']
            if item['bfzcj']==item['cj']:
                s['level']=None
            else:
                s['level']=item['cj']
            s['xf']=item['xf']
            s['jd']=item['jd']
            s['kcxz']=item['kcxzmc']
            s['kch']=item['kch_id']
            all_score.append(s)
        return all_score

    def get_now_point(self,cookie):
        url = 'http://jwzx.zjxu.edu.cn/jwglxt/cjcx/cjcx_cxDgXscj.html'
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        param = {
            'gnmkdm': 'N305005',
            'doType': 'query',
            'su': self.yhm
        }
        data = {
            'xnm': '2020',
            'xqm': '12',
            '_search': 'false',
            'nd': str(int(time() * 1000)),
            'queryModel.showCount': '30',
            'queryModel.currentPage': '1',
            'queryModel.sortName': 'xf',
            'queryModel.sortOrder': 'desc',
            'time': '1'
        }
        data=self.term_judge(data)
        q = self.querypage(head, param, data)
        if q == None: return None

        return q
    def get_point(self,cookie):
        url='http://jwzx.zjxu.edu.cn/jwglxt/cjcx/cjcx_cxDgXscj.html'
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        param={
            'gnmkdm' : 'N305005' ,
            'doType':'query' ,
            'su' : self.yhm
        }
        data={
            'xnm':'2020',
            'xqm':'12',
            '_search':'false',
            'nd':str(int(time()*1000)),
            'queryModel.showCount':'30',
            'queryModel.currentPage': '1',
            'queryModel.sortName': 'xf',
            'queryModel.sortOrder': 'desc',
            'time':'1'
        }
        start_year=int(self.yhm[:4])
        s=[]
        for year in range(start_year,start_year+6):
            for xq in (3,12):#不知道为啥3代表第一学期，12代表第二学期
                data['xnm']=str(year)
                data['xqm']=str(xq)
                q=self.querypage(head,param,data)
                if q==None:return None
                s+=q
        return s
    def calcu_gpa(self,score_list):
        gpa,xf,avg=0,0,0
        for score in score_list:
            if score['kcxz']!='公共选修课' and score['kch'][:2]!='TY':
                if float(score['jd'])==0.0:
                    continue
                gpa+=float(score['jd'])*float(score['xf'])
                xf+=float(score['xf'])
                avg+=float(score['score'])*float(score['xf'])
        #print('----------')
        print(xf)
        if xf==0:
            return 0,0,0
        else:
            return gpa/xf,avg/xf,xf

    def get_gpa(self,cookie ,flag):#1表示总,2表示学年,3表示本学期
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        param = {
            'gnmkdm': 'N305005',
            'doType': 'query',
            'su': self.yhm
        }
        data = {
            'xnm': '2020',
            'xqm': '12',
            '_search': 'false',
            'nd': str(int(time() * 1000)),
            'queryModel.showCount': '30',
            'queryModel.currentPage': '1',
            'queryModel.sortName': 'xf',
            'queryModel.sortOrder': 'desc',
            'time': '1'
        }
        score_list=[]
        if flag==1:
            start_year=int(self.yhm[:4])
            for year in range(start_year,start_year+6):
                for xq in (3,12):
                    data['xnm']=str(year)
                    data['xqm']=str(xq)
                    res=self.querypage(headers=head,params=param,data=data)
                    if res==None:
                        return None,None,None
                    score_list+=res
            return self.calcu_gpa(score_list)

        if flag==2:
            data = self.term_judge(data)
            for xq in (3,12):
                data['xqm']=str(xq)
                res = self.querypage(headers=head, params=param, data=data)
                if res == None:
                    return None, None, None
                score_list += res
            return self.calcu_gpa(score_list)

        if flag==3:
            data = self.term_judge(data)
            score_list = self.querypage(headers=head, params=param, data=data)
            if score_list == None:
                return None, None, None
            return self.calcu_gpa(score_list)

    def get_schedule(self,cookie):
        #获取年份和月份来爬固定学期的课表
        url='http://jwzx.zjxu.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html'
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        param = {
            'gnmkdm': 'N253508',
            #'doType': 'query',
            'su': self.yhm
        }
        data = {
            'xnm': '2020',
            'xqm': '12',
            'kzlx':'ck',
        }
        data=self.term_judge(data)
        p=self.s.post(url,params=param,data=data,headers=head,verify=False)
        try:
            query_data=json.loads(p.text)['kbList']
        except:
            return None

        res=[]
        for item in query_data:
            s={}
            s['place']=item['cdmc']
            s['name']=item['kcmc']
            s['weekday']=item['xqj']
            s['section']=item['jc']
            s['range']=item['zcd']
            s['xz']=item['kcxz']
            s['xf']=item['xf']
            res.append(s)
        return res

    def time_judge(self,exam_time):
        x = localtime(time())
        now_time = strftime('%Y-%m-%d', x)
        exam_time=re.search('\((.*?)\)',exam_time).group(1)
        if now_time > exam_time:
            return False
        return  True
        pass

    def get_exam(self,cookie,all):
        url='http://jwzx.zjxu.edu.cn/jwglxt/kwgl/kscx_cxXsksxxIndex.html'
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html?time=1598366187884",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        param = {
            'doType': 'query',
            'gnmkdm': 'N358105',
            'su': self.yhm
        }

        data = {
            'xnm': '2020',
            'xqm': '12',
            'ksmcdmb id': '',
            'kch': '',
            'kc': '',
            'ksrq': '',
            'kkbm_id': '',
            'ksmc': '',
            '_search': 'false',
            'nd': str(int(time() * 1000)),
            'queryModel.showCount': '30',
            'queryModel.currentPage': '1',
            'queryModel.sortName': 'kssj',
            'queryModel.sortOrder': 'asc',
            'time': '1'
        }
        data=self.term_judge(data)
        p=self.s.post(url,params=param,headers=head,data=data,verify=False)
        try:
            query_data = json.loads(p.text)['items']
        except:
            return None

        res=[]
        for item in query_data:
            s={}
            s['name']=item['kcmc']
            s['time']=item['kssj']
            s['place']=item['cdmc']
            s['site']=item['zwh']
            if self.time_judge(s['time']) or all:
                res.append(s)
            #print(s)
        return res

    def get_arg(self,arg_list, regx, text) -> dict:
        data = {}
        for arg in arg_list:
            res = re.search(regx.format(arg, arg), text)
            if res != None:
                data[arg] = res.group(1)
                # print('"{0}"="{1}"'.format(arg,data[arg]))
            else:
                data[arg] = '0'
        return data

    def query_xkxx(self,cookie):
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        url = 'http://jwzx.zjxu.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default&su=' + self.yhm
        p = self.s.get(url, headers=head,verify=False)
        xkxx = []
        try:
            xkkz_id = re.findall('onclick="queryCourse\(this,(.*?)\)"', p.text)

            for i in xkkz_id:
                #print(i)
                data = eval('[' + i + ']')
                flag=1
                for item in xkxx :
                    if item[1]==data[1]:
                        flag=0
                        break
                if flag:
                    xkxx.append(data)

            #print(xkxx)
        except:
            pass
        try:
            xxk=re.search('<input type="hidden" name="firstXkkzId" id="firstXkkzId" value="(.*?)"/>',p.text).group(1)
            kklxdm=re.search('<input type="hidden" name="firstKklxdm" id="firstKklxdm" value="(.*?)"/>',p.text).group(1)
            xkxx.append([kklxdm,xxk])
        except:
            print('No!')
            f=open('log.log','w+')
            print(p.text,file=f)
            f.close()
            pass
        return xkxx, p.text

    def do_pre_work(self, cookie, xkkz_id):
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }

        data = {
            'xkkz_id': xkkz_id,
            'xszxzt': '1',
            'kspage': '0',
            'jspage': '0'
        }
        url = 'http://jwzx.zjxu.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbDisplay.html?gnmkdm=N253512&su=' + self.yhm
        r = self.s.post(url, headers=head, data=data,verify=False)
        return r.text

    def query_kch(self,cookie, text, kklxdm,xkkz_id):
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        regx = '<input type="hidden" name="{0}" id="{1}" value="(.*?)"'
        arg_list1 = ['rwlx', 'xkly', 'bklx_id', 'xqh_id', 'zyh_id', 'zyfx_id', 'njdm_id',
                     'bh_id', 'xbm', 'xslbdm', 'ccdm', 'xsbj', 'sfkknj', 'sfkkzy', 'kzybkxy',
                     'sfznkx', 'zdkxms', 'sfkxq', 'sfkcfx', 'kkbk', 'kkbkdj', 'sfkgbcx',
                     'sfrxtgkcxd', 'tykczgxdcs', 'xkxnm', 'xkxqm', 'rlkz', 'xkzgbj', 'kspage',
                     'jspage', 'jxbzb'
                     ]

        try:
            jg_id = re.search(regx.format('jg_id_1', 'jg_id_1'), text).group(1)
        except:
            return None
        data = self.get_arg(arg_list1, regx, text)
        data['kklxdm'] = kklxdm
        data['jg_id'] = jg_id
        data['yl_list[0]'] = '1'
        url = 'http://jwzx.zjxu.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512&su=' + self.yhm
        data['kspage'] = '1'
        data['jspage'] = '10'
        data['xkkz_id']=xkkz_id
        p = self.s.post(url, headers=head, data=data,verify=False)
        try:
            res = json.loads(p.text)['tmpList']
            ans = []
            for kc in res:
                data = {}
                data['name'] = kc['kcmc']
                data['kch'] = kc['kch']
                data['kch_id'] = kc['kch_id']
                data['xf'] = kc['xf']
                data['xkkz_id']=xkkz_id
                # data['hash'] = kc['jxb_id']
                if data not in ans:
                    ans.append(data)
            return ans
        except:
            return None

    def query_cls(self, cookie, kch, xkkz_id,kklxdm, text, yuliang='1'):
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        url = 'http://jwzx.zjxu.edu.cn/jwglxt/xsxk/zzxkyzbjk_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512&su='+self.yhm
        arg_list2 = ['rwlx', 'xkly', 'bklx_id', 'xqh_id', 'zyh_id', 'zyfx_id', 'njdm_id',
                     'bh_id', 'xbm', 'xslbdm', 'ccdm', 'xsbj', 'sfkknj', 'sfkkzy', 'kzybkxy',
                     'sfznkx', 'zdkxms', 'sfkxq', 'sfkcfx', 'kkbk', 'kkbkdj', 'xkxnm', 'xkxqm', 'rlkz',
                     ]
        regx = '<input type="hidden" name="{0}" id="{1}" value="(.*?)"'
        jg_id = re.search(regx.format('jg_id_1', 'jg_id_1'), text).group(1)

        data = self.get_arg(arg_list2, regx, text)
        #print('kklxdm:{0}'.format(kklxdm))
        data['kklxdm'] = kklxdm
        data['jg_id'] = jg_id
        data['yl_list[0]'] = yuliang
        data['xkkz_id'] = xkkz_id
        data['kch_id'] = kch

        p = self.s.post(url, headers=head, data=data,verify=False)
        try:
            #print(p.text)
            res = json.loads(p.text)
            ans=[]
            for cls in res:
                data={}
                data['teacher']=re.search('/(.*?)/',cls['jsxx']).group(1)
                data['place']=cls['jxdd'].replace('<br/>','\n')
                data['time']=cls['sksj'].replace('<br/>','\n')
                data['jxb_id']=cls['jxb_id']
                data['do_jxb_id']=cls['do_jxb_id']
                ans.append(data)
            return ans
        except:
            return None

    def xuanke(self, cookie, cls_item, xkkz_id, text, kch_id):
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        regx = '<input type="hidden" name="{0}" id="{1}" value="(.*?)"'
        url = 'http://jwzx.zjxu.edu.cn/jwglxt/xsxk/zzxkyzbjk_xkBcZyZzxkYzb.html?gnmkdm=N253512&su=202059545308'
        arglist = [
            'rwlx', 'rlkz', 'rlzlkz', 'sxbj', 'xxkbj', 'qz', 'cxbj',
            'njdm_id', 'zyh_id', 'kklxdm', 'xklc', 'xkxnm', 'xkxqm'
        ]
        data = self.get_arg(arglist, regx, text)
        data['kch_id'] = kch_id
        data['xkkz_id'] = xkkz_id
        data['jxb_ids'] = cls_item['do_jxb_id']
        p = self.s.post(url, headers=head, data=data,verify=False)
        try:
            res = json.loads(p.text)
            if res['flag'] == '1':
                return True,'选课成功'
            else:
                return False,res['msg']
        except:
            return None,None

    def tuike(self, cookie, kch, xkkz_id,kklxdm, text):
        head = {
            "Referer": "http://jwzx.zjxu.edu.cn/jwglxt/xtgl/login_slogin.html",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
            "Accept-Encoding": "gzip, deflate",
            "Host": "jwzx.zjxu.edu.cn",
            "Connection": "Keep-Alive",
            'Cookie': cookie
        }
        url = 'http://jwzx.zjxu.edu.cn/jwglxt/xsxk/zzxkyzb_tuikBcZzxkYzb.html?gnmkdm=N253512&su='+self.yhm
        tmp={}
        tmp=self.term_judge(tmp)
        kch_list=self.query_kch(cookie,text,kklxdm,xkkz_id)
        flag=False
        for kc in kch_list:
            if kch==kc['kch']:
                kch=kc['kch_id']
                flag = True
                break
        if not flag:
            return None

        data = {}
        data['kc_id'] = kch
        data['txbsfrl'] = '0'
        data['xkxnm'] = tmp['xnm']
        data['xkxqm'] = tmp['xqm']
        cls_list=self.query_cls(cookie,kch,xkkz_id,kklxdm,text,'1') + self.query_cls(cookie,kch,xkkz_id,kklxdm,text,'0')
        #print(cls_list)
        if cls_list==None:
            return None
        if len(cls_list)==0:
            return None
        for cls_item in cls_list:
            data['jxb_ids'] = cls_item['do_jxb_id']
            p = self.s.post(url, headers=head, data=data,verify=False)
            #print(p.text)
        return p.text
if __name__=='__main__':
    s =  session('','')
    #cookie=s.login()
    xkkz_id,text=s.do_pre_work()
    res=s.query_kch(cookie,text)
    res=s.query_cls(cookie,'24837',xkkz_id,text)
    for x in res:
        print(x)



    #s.get_point(cookie)
    #print(cookie)


