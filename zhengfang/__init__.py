from nonebot.rule import to_me
from nonebot.plugin import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (Bot, Message, MessageEvent, MessageSegment,
                                     unescape)
from nonebot.rule import to_me
import os
import json
from time import sleep,time
from random import randint,seed
from .process import *

login_user = on_command("账号",to_me())
@login_user.handle()
async def login_user(bot: Bot,event: MessageEvent):
    file_name = str(event.get_user_id())
    file_judge(file_name)
    user=str(event.get_message())[2:].replace(' ','')
    if not user.isdigit():
        await bot.send(message='不应当含有非数字字符\n也许是多打了空格？', event=event)
        return

    user_info = get_data(file_name)
    user_info['username'] = user
    update_file(path+file_name,user_info)
    await bot.send(message='账号修改成功', event=event)

login_pwd = on_command('密码',to_me())
@login_pwd.handle()
async def login_pwd(bot: Bot,event: MessageEvent):

    file_name = str(event.get_user_id())
    file_judge(file_name)
    pwd = str(event.get_message())[2:].replace(' ','')
    if len(pwd) < 6:
        await bot.send(message='请检查你的密码', event=event)
        return

    if '{' in pwd or '}' in pwd:
        await bot.send(message='Serialize me?', event=event)
        return

    user_info = get_data(file_name)
    user_info['passwd'] = pwd
    update_file(path+file_name,user_info)
    await bot.send(message='密码修改成功', event=event)

login_event = on_command('login',to_me())
@login_event.handle()
async def login_event(bot: Bot,event: MessageEvent):
    await bot.send(message='login命令已不再使用，直接查询即可', event=event)


tail='; MC_user_setting={"api":0,"auto":0}'
login_score = on_command('查分',to_me())
@login_score.handle()
async def login_score(bot: Bot,event: MessageEvent):

    file_name = str(event.get_user_id())
    data = query_judge(file_name)
    if type(data) == type(''):
        await bot.send(message=Message(data), event=event)
        return

    user_info = data
    s = session(user_info['username'], user_info['passwd'])
    arg = str(event.get_message())[2:].replace(' ','')
    if arg=='now' or arg.replace(' ','')=='':
        query_data=s.get_now_point(user_info['cookie']+tail)
        if query_data==None:
            await bot.send(message='cookie已过期，正在重新登录获取...', event=event)
            x,msg=login(file_name)
            await bot.send(message=Message(msg), event=event)
            if x:
                user_info = query_judge(file_name)
                query_data = s.get_now_point(user_info['cookie'] + tail)
            else:
                return

        await bot.send(message='成功获取分数', event=event)
        if len(query_data):
            for item in query_data:
                await bot.send(message=Message(handle_score(item)), event=event)
                sleep(0.5)
        else:
            await bot.send(message='您本学期还没有考试成绩', event=event)
    else:
        query_data=s.get_point(user_info['cookie']+tail)
        if query_data==None:
            await bot.send(message='cookie已过期，正在重新登录获取...', event=event)
            x, msg = login(file_name)
            await bot.send(message=Message(msg), event=event)
            if x:
                user_info = query_judge(file_name)
                query_data = s.get_point(user_info['cookie'] + tail)
            else:
                return

        await bot.send(message='成功获取分数', event=event)
        if 'all' in arg:
            for item in query_data:
                await bot.send(message=Message(handle_score(item)), event=event)
                sleep(0.5)
        else:
            flag=True
            for item in query_data:
                if match(arg,item['name']):
                    flag=False
                    print('ok in '+item['name'])
                    await bot.send(message=Message(handle_score(item)), event=event)
                    sleep(0.5)
            if flag:
                await bot.send(message='并没有找到带有关键词："{}"的考试成绩\n请检查一下输入'.format(arg), event=event)

class_query = on_command("课表")
@class_query.handle()
async def class_query(bot: Bot,event: MessageEvent):
    file_name = str(event.get_user_id())
    data = query_judge(file_name)
    if type(data) == type(''):
        await bot.send(message=Message(data), event=event)
        return

    user_info = data
    s = session(user_info['username'], user_info['passwd'])
    data=s.get_schedule(user_info['cookie'])
    if data==None:
        await bot.send(message='cookie已过期，正在重新登录获取...', event=event)
        x, msg = login(file_name)
        await bot.send(message=Message(msg), event=event)
        if x:
            user_info = query_judge(file_name)
            data = s.get_schedule(user_info['cookie'])
        else:
            return


    await bot.send(message='成功获取课表', event=event)
    arg=str(event.get_message())
    if arg=='all':
        for cls in data:
            await bot.send(message=Message(handle_class(cls)), event=event)
            sleep(0.5)
    else:
        weekday=0
        for num in arg:
            if num.isdigit():
                weekday=int(num)
                break
        if weekday==0:
            await bot.send(message='用法:课表 [x] 查询星期x的所有课或者\nclass all查询本学期总课表', event=event)
            return
        for cls in data:
            if int(cls['weekday'])==weekday:
                await bot.send(message=Message(handle_class(cls)), event=event)
                sleep(0.5)
    seed(time())
    x=randint(1,100)
    if x<10:
        await bot.send(message=Message('想逃课之前还请看看学分有多少([CQ:face,id=277]'), event=event)
    return

exam_query = on_command('考试',to_me())
@exam_query.handle()
async def exam_query(bot: Bot,event: MessageEvent):

    file_name = str(event.get_user_id())
    data=query_judge(file_name)
    if type(data)==type(''):
        await bot.send(message=Message(data), event=event)
        return

    user_info=data
    s = session(user_info['username'], user_info['passwd'])
    arg=str(event.get_message())[2:]
    data = s.get_exam(user_info['cookie'],arg=='all')
    if data==None:
        await bot.send(message='cookie已过期，正在重新登录获取...', event=event)
        x, msg = login(file_name)
        await bot.send(message=Message(msg), event=event)
        if x:
            user_info = query_judge(file_name)
            data = s.get_exam(user_info['cookie'],arg=='all')
        else:
            return

    if len(data):
        await bot.send(message='成功获取考试信息', event=event)
        for exam in data:
            await bot.send(message=Message(handle_exam(exam)), event=event)
            sleep(0.5)
    else:
        if end_judge():
            await bot.send(message='❀完结撒花❀\n所有考试都结束啦！！\n快乐的假期也不要忘了学习哦', event=event)
        else:
            await bot.send(message='未查询到本学期的考试', event=event)

xuanke_query = on_command('选课',to_me())
@xuanke_query.handle()
async def xuanke_query(bot: Bot,event: MessageEvent):
    file_name = str(event.get_user_id())
    data = query_judge(file_name)
    if type(data) == type(''):
        await bot.send(message=Message(data), event=event)
        return

    user_info = data
    s = session(user_info['username'], user_info['passwd'])
    arg = str(event.get_message())[3:]
    xkxx, p_text = s.query_xkxx(user_info['cookie'])

    print(xkxx)
    if xkxx==None or not len(xkxx):
        await bot.send(message='cookie已过期，正在重新登录获取...', event=event)
        x, msg = login(file_name)
        await bot.send(message=Message(msg), event=event)
        if x:
            user_info = query_judge(file_name)
            xkxx, p_text = s.query_xkxx(user_info['cookie'])
        else:
            return



    arg=delete_space(arg)

    if arg=='':#课程号查询
        await bot.send(message='成功获取选课信息', event=event)

        res = []
        for i in xkxx:
            r_text = s.do_pre_work(user_info['cookie'], i[1])
            res += s.query_kch(user_info['cookie'], p_text + r_text, i[0],i[1])
        if res == None or len(res)==0:
            await bot.send(message='当前可能并不在选课阶段', event=event)
            return

        res=erase_equal(res)
        
        for item in res:
            await bot.send(message=Message(handle_kch(item)), event=event)
            sleep(0.5)
        return

    if arg.find(' ')== -1:#查一门课的具体信息
        for xiaoji in xkxx:
            r_text = s.do_pre_work(user_info['cookie'], xiaoji[1])
            kch_list=s.query_kch(user_info['cookie'], p_text + r_text, xiaoji[0],xiaoji[1])

            if kch_list==None:
                await bot.send(message='当前可能并不在选课阶段', event=event)
                return

            flag=False
            for kch in kch_list:
                #print('compare {0}:{1}'.format(kch['kch'],arg))
                if kch['kch'].__eq__(arg):
                    #print('success!!!!!')
                    flag=True
                    kcmc=kch['name']
                    kch_id=kch['kch_id']
                    xkkz_id=kch['xkkz_id']
                    break

            if not flag:
                continue

            res=s.query_cls(user_info['cookie'],kch_id,xiaoji[1],xiaoji[0],p_text+r_text)

            print(res)
            if res == None:
                continue

            if not len(res):
                continue

            num=1
            for item in res:
                await bot.send(message=Message(handle_cls(item,kcmc,num)), event=event)
                sleep(0.5)
                num+=1
            return
        await bot.send(message=Message('错误的课程号{0}'.format(arg)), event=event)
        return

    kch=arg[:arg.find(' ')]

    for xiaoji in xkxx:
        r_text = s.do_pre_work(user_info['cookie'], xiaoji[1])
        kch_list = s.query_kch(user_info['cookie'], p_text + r_text, xiaoji[0],xiaoji[1])

        if kch_list==None:
            await bot.send(message='当前可能并不在选课阶段', event=event)
            return
        flag = False
        for kc in kch_list:
            if kc['kch'] == kch:
                flag = True
                kcmc = kc['name']
                kch_id = kc['kch_id']
                break
        if not flag:
            continue

        res = s.query_cls(user_info['cookie'], kch_id, xiaoji[1],xiaoji[0], p_text+r_text)
        print(res)
        if res == None:
            await bot.send(message='获取信息失败，请联系开发者解决', event=event)
            return

        if not len(res):
            await bot.send(message='该课程没有找到有效的记录', event=event)
            return

        try:
            num=int(arg[arg.find(' ')+1:])
        except:
            await bot.send(message='请输入正确的序号', event=event)
            return

        if len(res)<num or num <=0 :
            await bot.send(message='该课程并没有找到序号为{0}的记录，请检查您的序号'.format(num), event=event)
            return

        flag,msg=s.xuanke(user_info['cookie'],res[num-1],xiaoji[1],p_text+r_text,kch_id)
        if flag==None:
            await bot.send(message='发现未知错误', event=event)
            return

        if flag:
            await bot.send(message='选课成功\n课程名称：'+kcmc, event=event)
            return
        else:
            await bot.send(message='选课发生错误，错误信息：{0}'.format(msg) + kcmc, event=event)
            return

tuike_query = on_command('退课',to_me())
@tuike_query.handle()
async def tuike_query(bot: Bot,event: MessageEvent):
    file_name = str(event.get_user_id())
    data = query_judge(file_name)
    if type(data) == type(''):
        await bot.send(message=Message(data), event=event)
        return
    user_info = data
    s = session(user_info['username'], user_info['passwd'])
    arg = str(event.get_message())[2:]
    xkxx, p_text = s.query_xkxx(user_info['cookie'])
    if xkxx==None:
        await bot.send(message='cookie已过期，正在重新登录获取...', event=event)
        x, msg = login(file_name)
        await bot.send(message=Message(msg), event=event)
        if x:
            user_info = query_judge(file_name)
            xkxx, p_text = s.query_xkxx(user_info['cookie'])
        else:
            return

    arg=delete_space(arg)
    for i in xkxx:
        r_text = s.do_pre_work(user_info['cookie'], i[1])
        res=s.tuike(user_info['cookie'],arg,i[1],i[0],p_text+r_text)
        if res==None:
            continue
        if res=='"1"':
            await bot.send(message='已退选所有课程号为{0}的课程'.format(arg), event=event)
            return
        else:
            await bot.send(message='未知的错误，请联系管理员', event=event)
            return
    await bot.send(message='课程号错误\n您输入的课程号：{0}'.format(arg), event=event)
    return

gpa_query = on_command(cmd='gpa',aliases={"GPA"})
@gpa_query.handle()
async def gpa_query(bot: Bot,event: MessageEvent):

    file_name = str(event.get_user_id())
    data = query_judge(file_name)
    if type(data) == type(''):
        await bot.send(message=Message(data), event=event)
        return
    user_info = data
    s = session(user_info['username'], user_info['passwd'])
    arg = str(event.get_message())[3:].replace(' ','')
    #print(arg)
    flag=3
    if arg=='all':flag=1
    elif arg=='year':flag=2
    print(flag)
    gpa,avg,xf=s.get_gpa(user_info['cookie'],flag)
    if gpa==None:
        await bot.send(message='cookie已过期，正在重新登录获取...', event=event)
        x, msg = login(file_name)
        await bot.send(message=Message(msg), event=event)
        if x:
            user_info = query_judge(file_name)
            gpa, avg, xf = s.get_gpa(user_info['cookie'], flag)
        else:
            return

    await bot.send(message=handle_gpa(gpa,avg,xf,flag), event=event)

