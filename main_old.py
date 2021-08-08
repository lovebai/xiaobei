import base64
import json
import os
import random
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header


# 小北学生 账号密码
USERNAME = ''
PASSWORD = ''
# 经纬度
LOCATION = ''
# 位置
COORD = ''
# 邮件开关
IS_EMAIL = ''
# 接收消息邮箱账号
EMAIL = ''
# 发送邮箱配置
E_HOST = ''
E_ACCOUNT = ''
E_PASS = ''


# 配置文件
CONF = 'config.conf'

# 基本链接
BASE_URL = "https://xiaobei.yinghuaonline.com/prod-api/"
# header
HEADERS = {
    "user-agent": "iPhone10,3(iOS/14.4) Uninview(Uninview/1.0.0) Weex/0.26.0 1125x2436",
    "accept": "*/*",
    "accept-language": "zh-cn",
    "accept-encoding": "gzip, deflate, br"
}


def is_open():
    import platform
    # 只在win系统下打开
    if platform.system() == 'Windows':
        reply = str(input("选择是否去获取经纬度，此操作会打开默认浏览器[Y/N]："))
        if reply == 'Y':
            import webbrowser
            webbrowser.open("https://api.xiaobaibk.com/api/map/")
        else:
            pass
    else:
        print("请在浏览器里打开链接获取经纬度：https://api.xiaobaibk.com/api/map/")


def is_email():
    print("开启邮件通知后可以收到打卡成功和失败通知，如果要开启的话是需要配置的，选择权在你^_^")
    reply = input("是否需要开启邮件通知[Y/N]:")
    if reply == 'N' or reply != "Y":
        return {}
    else:
        email = str(input("请输入要接收消息的邮箱账号："))
        host = str(input("请输入SMTP服务器地址："))
        from_mail = str(input("请输入发送通知邮箱账号："))
        password = str(input("请输入发送通知邮箱账号的密码："))
        return {'email': email, 'host': host, 'send_mail': from_mail, 'password': password}


path = os.getcwd() + '\\' + CONF
if not os.path.exists(path):
    USERNAME = str(input("请输入小北学生账号："))
    PASSWORD = str(input("请输入小北学生密码："))
    is_open()
    LOCATION = str(input("请将您所复制的经纬度粘贴到此处："))
    COORD = str(input("请将您所在的区域【如：中国-云南省-昆明市-官渡区】："))
    rep = is_email()
    if len(rep) == 0:
        IS_EMAIL = 0
    else:
        IS_EMAIL = 1
        EMAIL = str(rep['email'])
        E_HOST = str(rep['host'])
        E_ACCOUNT = str(rep['send_mail'])
        E_PASS = str(rep['password'])
    PASSWORD = str(base64.b64encode(PASSWORD.encode()).decode())
    conf = {
        'user': USERNAME,
        'pass': PASSWORD,
        'location': LOCATION,
        'coord': COORD,
        'is_mail': IS_EMAIL,
        'to': EMAIL,
        'host': E_HOST,
        'from': E_ACCOUNT,
        'pwd': E_PASS
    }
    try:
        fp = open(path, 'w+')
        fp.write(json.dumps(conf))
    except IOError:
        print("IO Error")
    else:
        fp.close()

else:
    try:
        con = open(path, 'r')
        data = json.loads(con.read())
    except IOError:
        print("IO Error")
    else:
        USERNAME = data['user']
        PASSWORD = data['pass']
        LOCATION = data['location']
        COORD = data['coord']
        IS_EMAIL = data['is_mail']
        EMAIL = data['to']
        E_HOST = data['host']
        E_ACCOUNT = data['from']
        E_PASS = data['pwd']
        con.close()


def get_param():
    # 体温随机为35.7~36.7
    temperature = str(random.randint(357, 367) / 10)
    # 107.807008,26.245838
    rand = random.randint(1111, 9999)
    # 经度
    location_x = LOCATION.split(',')[0].split('.')[0] + '.' + LOCATION.split(',')[0].split('.')[1][0:2] + str(rand)
    # 纬度
    location_y = LOCATION.split(',')[1].split('.')[0] + '.' + LOCATION.split(',')[1].split('.')[1][0:2] + str(rand)
    location = location_x + ',' + location_y
    return {
        "temperature": temperature,
        "coordinates": COORD,
        "location": location,
        "healthState": "1",
        "dangerousRegion": "2",
        "dangerousRegionRemark": "",
        "contactSituation": "2",
        "goOut": "1",
        "goOutRemark": "",
        "remark": "无",
        "familySituation": "1"
    }


def send_mail(context):
    sender = E_ACCOUNT
    receivers = [EMAIL]
    message = MIMEText(context, 'plain', 'utf-8')
    message['From'] = Header("小白", 'utf-8')
    message['To'] = Header("白嫖怪", 'utf-8')
    subject = '每日打卡状态提醒'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(E_HOST, 25)
        smtpObj.login(E_ACCOUNT, E_PASS)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("Succeed!")
    except smtplib.SMTPException:
        print("Error!")


if __name__ == '__main__':
    # Url
    # 滑动验证
    captcha = BASE_URL + 'captchaImage'
    # 登录
    login = BASE_URL + 'login'
    # 打卡
    health = BASE_URL + 'student/health'

    # post method return 500 , So use the get method
    # data:   {"msg":"操作成功","img":"xxxxxx","code":200,"showCode":"NM6B","uuid":"4f72776b789b44d796722037ba7a1ff0"}
    response = requests.get(url=captcha, headers=HEADERS).text
    # 取得uuid及showCode
    uuid = json.loads(response)['uuid']
    showCode = json.loads(response)['showCode']

    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "code": showCode,
        "uuid": uuid
    }

    # 登录测试
    # success return {"msg":"操作成功","code":200,"token":"eyJhb....."}
    # error return {"msg":"用户不存在/密码错误","code":500}
    res = requests.post(url=login, headers=HEADERS, json=data).text
    code = json.loads(res)['code']
    msg = json.loads(res)['msg']

    if code != 200:
        print("Sorry! Login failed! Error：" + msg)
        # 发送邮件
        if IS_EMAIL == 1:
            send_mail("登录失败，失败原因：" + msg)
    else:
        print("登录成功！")

        # HEADERS.update({'authorization', token})
        # 换个方法
        HEADERS['authorization'] = json.loads(res)['token']

        health_param = get_param()

        respond = requests.post(url=health, headers=HEADERS, json=health_param).text
        # error return {'msg': None, 'code': 500}
        # succeed return {'msg': '操作成功', 'code': 200}
        status = json.loads(respond)['code']
        if status == 200:
            print("恭喜您打卡成功了！")
            if IS_EMAIL == 1:
                send_mail("更新您今天打卡成功啦^_^")
        else:
            print("Error：" + json.loads(respond)['msg'])
            if IS_EMAIL == 1:
                send_mail("抱歉打卡失败了，原因未知，请自信手动打卡，谢谢>_<")
