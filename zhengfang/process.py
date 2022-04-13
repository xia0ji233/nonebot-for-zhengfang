import os
import json
from .login import *
from hashlib import md5
from time import  time

path='./src/plugins/zhengfang/user/'

def match(str1,str2):
    for i in str1:
        if i not in str2:
            return False
    return True

def file_judge(qq_number):
    if not os.path.exists(path):
        os.system('mkdir '+path)
    if not os.path.exists(path+qq_number):
        os.system('touch '+path+qq_number)
        os.system('echo {\\"username\\": \\"\\",\\"passwd\\":\\"\\",\\"cookie\\":\\"JSESSIONID=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\"} >'+ path+qq_number)
        return False
    return True

def get_data(qq_number):
    f = open(path + qq_number, 'r')
    try:
        user_info = json.loads(f.readline())
    except:
        os.system('echo {\\"username\\": \\"\\",\\"passwd\\":\\"\\",\\"cookie\\":\\"JSESSIONID=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\"} >' + path + qq_number)
        user_info = json.loads(f.readline())
    f.close()
    return user_info

def query_judge(qq_number):
    if not os.path.exists(path + qq_number):
        return '您还没有创建账号'

    user_info = get_data(qq_number)
    if user_info['username'] == '' or user_info['passwd'] == '':
        return '您还没有输入账号或密码'

    return user_info

def update_file(file_path,user_data):
    f=open(file_path,'w')
    print(str(user_data).replace('\'', '"'), file=f,end='')#把单引号换了
    f.close()

def login(qq_number):
    if not file_judge(qq_number):
        return False,'您还没有输入账号或密码'


    user_info=get_data(qq_number)
    s=session(user_info['username'],user_info['passwd'])
    cookie=s.login()
    if cookie==None:
        return False,'账号或密码错误，请检查'

    user_info['cookie'] = cookie
    update_file(path+qq_number,user_info)
    info=s.get_info(cookie)
    message='登录成功\n姓名:{}\n班级:{}'.format(info['name'],info['class'])
    return True,message

def handle_score(score_item):
    message = '---成绩信息---\n查询的课程：' + score_item['name'] + '\n'
    message += '课程成绩：' + score_item['score'] + '\n'
    if score_item['level'] == None:
        message += '课程等级：' + '无' + '\n'
    else:
        message += '课程等级：' + score_item['level'] + '\n'
    message += '课程绩点：' + score_item['jd'] + '\n'
    message += '课程学分：' + score_item['xf'] + '\n'
    message += md5(str(time()).encode()).hexdigest()[:8]
    return message

def handle_class(class_item):
    hanzi = '一二三四五六七'
    message = '---课表信息---\n课程名称：' + class_item['name'] + '\n'
    message += '教学地点：' + class_item['place'] + '\n'
    message += '第几周：' + class_item['range'] + '\n'
    message += '星期几：星期' + hanzi[int(class_item['weekday']) - 1] + '\n'
    message += '具体时间：' + class_item['section'] + '\n'
    message += '课程性质：' + class_item['xz'] + '\n'
    message += '学分：' + class_item['xf'] + '\n'
    message += md5(str(time()).encode()).hexdigest()[:8]
    return message

def handle_exam(exam_item):
    message = '---考试信息---\n考试名称：'+exam_item['name']+'\n'
    message += '考试时间：' + exam_item['time'] + '\n'
    message += '考试地点：' + exam_item['place'] + '\n'
    message += '座位号：' + exam_item['site'] + '\n'
    message += md5(str(time()).encode()).hexdigest()[:8]
    return message

def handle_kch(kch_item):
    message = '---选课信息---\n选修课名称：'+kch_item['name'] + '\n'
    message += '课程学分：'+kch_item['xf'] + '\n'
    message += '课程号：' +kch_item['kch'] + '\n'
    message += md5(str(time()).encode()).hexdigest()[:8]
    return message

def handle_cls(cls_item,kcmc,num):
    message = '---具体选课信息---\n选修课名称：' + kcmc+ '\n'
    message += '序号：' + str(num) + '\n'
    message += '课程教师：'+cls_item['teacher']+'\n'
    message += '上课时间：\n'+cls_item['time'] + '\n'
    message += '上课地点：\n'+cls_item['place'] + '\n'
    message += md5(str(time()).encode()).hexdigest()[:8]
    return message

def end_judge():
    x = localtime(time())
    month = x.tm_mon
    if month >= 1 and month < 3:
        return True
    if month >= 6 and month < 9:
        return True
    return False

def handle_gpa(gpa,avg,xf,flag):
    message ='---GPA信息---\n总加权平均分：'+'{:.3f}'.format(avg) + '\n'
    message +='总GPA：'+'{:.3f}'.format(gpa) + '\n'
    message +='总学分：'+'{:.1f}'.format(xf) + '\n'
    message += md5(str(time()).encode()).hexdigest()[:8]
    if flag==2:
        message=message.replace('总','本学年')
    elif flag==3:
        message=message.replace('总','本学期')
    return message

def delete_space(arg):
    while len(arg):
        if arg[0] == ' ':
            arg = arg[1:]
        else:
            break
    for i in range(len(arg))[::-1]:
        if arg[i] == ' ':
            arg = arg[:-1]
        else:
            break
    return arg

def erase_equal(table):
    rubbish=[]
    res=[]
    for i in table:
        st=i['kch_id']
        if st in rubbish:
            continue
        rubbish.append(st)
        res.append(i)
    return res
