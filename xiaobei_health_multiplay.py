

import base64
from email import message
import json
import os
import random
from time import sleep
from matplotlib.pyplot import title
from numpy import array
import requests
import time

# 批量打卡
array = [
    ["用户1", "密码1"],
    ["用户2", "密码2"],
]

# TGbot推送
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHATID = os.getenv("TG_CHATID")
TG_URL = os.getenv("TG_URL")
# server酱
SENDKEY = os.getenv("XB_SENDKEY")
# 企业微信应用
WX_APP = os.getenv("XB_WXAPP")

# API地址
BASE_URL = "https://xiaobei.yinghuaonline.com/xiaobei-api/"
captcha_url = BASE_URL + 'captchaImage'
# 登录
login_url = BASE_URL + 'login'
# 打卡
health_url = BASE_URL + 'student/health'

# 小北学生 账号密码
# USERNAME = ""
# PASSWORD = ""

# 东区宿舍 经纬度
LOCATION = "114.340863,30.347289"
# 位置，可选通过接口获取
COORD = "中国-湖北省-武汉市-江夏区"

# header 请求头
HEADERS = {
    "user-agent": "iPhone10,3(iOS/14.4) Uninview(Uninview/1.0.0) Weex/0.26.0 1125x2436",
    "accept": "*/*",
    "accept-language": "zh-cn",
    "accept-encoding": "gzip, deflate, br"
}


def sc_send(title, message):
    baseUrl = 'https://sctapi.ftqq.com/'+SENDKEY+'.send'
    resp = None
    data = {
        "title": title,
        "desp": message
    }
    try:
        resp = requests.post(baseUrl, data=data).text
        # {"code":0,"message":"","data":{"pushid":"35319564","readkey":"SCT1c4Qpzp0F9u7","error":"SUCCESS","errno":0}}
    except:
        print("server酱通知失败了")
    resp = json.loads(resp)
    if resp['code'] != 0:
        print(resp['message'])


def tg_send(context):
    bot_token = TG_BOT_TOKEN
    chat_id = TG_CHATID
    if not bot_token or not chat_id:
        print("未设置bot_token或chat_id")
        return
    if TG_URL:
        url = f"{TG_URL}/bot{TG_BOT_TOKEN}/sendMessage"
    else:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'chat_id': str(TG_CHATID), 'text': f'{context}',
               'disable_web_page_preview': 'true'}
    try:
        response = requests.post(url=url, headers=headers, params=payload)
    except:
        "TG推送失败"
    else:
        "TG推送完成"
# 一言


def yiyan():
    try:
        txt = requests.get("https://api.xiaobaibk.com/api/yiyan.php").text
    except:
        txt = '随言获取失败，不清楚什么问题，问问作者吧'
    return txt


def wxapp_notify(content, title='小北成功打卡通知'):
    app_params = WX_APP.split(',')
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        'corpid': app_params[0],
        'corpsecret': app_params[1],
    }
    try:
        response = requests.post(
            url=url, headers=headers, data=json.dumps(payload), timeout=15).json()
    except:
        print("微信通知发送不成功！")
        os._exit(0)
    accesstoken = response["access_token"]
    content = "打卡情况：[" + content + "]\n打卡位置：[" + COORD + \
        "]\n打卡日期：[" + time.strftime("%Y-%m-%d") + "]\n随言：["+yiyan()+"]"
    html = content.replace("\n", "<br/>")
    options = {
        'msgtype': 'mpnews',
        'mpnews': {
            'articles': [
                {
                    'title': title,
                    'thumb_media_id': f'{app_params[4]}',
                    'author': '小白',
                    'content_source_url': '',
                    'content': f'{html}',
                    'digest': f'{content}'
                }
            ]
        }
    }

    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={accesstoken}"
    data = {
        'touser': f'{app_params[2]}',
        'agentid': f'{app_params[3]}',
        'safe': '0'
    }
    data.update(options)
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, headers=headers,
                             data=json.dumps(data)).json()

    if response['errcode'] == 0:
        print('企业微信应用通知成功！')
    else:
        print('企业微信应用通知失败！')


def get_health_param(coord):
    # 体温随机为35.8~36.7
    temperature = str(random.randint(358, 367) / 10)
    # 107.807008,26.245838
    rand = random.randint(1111, 9999)
    # 经度
    location_x = LOCATION.split(',')[0].split(
        '.')[0] + '.' + LOCATION.split(',')[0].split('.')[1][0:2] + str(rand)
    # 纬度
    location_y = LOCATION.split(',')[1].split(
        '.')[0] + '.' + LOCATION.split(',')[1].split('.')[1][0:2] + str(rand)
    location = location_x + ',' + location_y
    return {
        "temperature": temperature,
        "coordinates": coord,
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


def xiaobei_update(username, password):
    print("\n"+username+"开始操作")
    # sleep(5)
    flag = False

    # 获取验证信息
    try:
        print("开始获取验证信息")
        response = requests.get(url=captcha_url, headers=HEADERS)

        uuid = response.json()['uuid']
        showCode = response.json()['showCode']
        print("验证信息获取成功")
    except:
        print("验证信息获失败")
        return False

    # 使用验证信息登录
    try:
        print("正在登录小北平台")
        response = requests.post(url=login_url, headers=HEADERS, json={
            "username": username,
            "password": str(base64.b64encode(password.encode()).decode()),
            "code": showCode,
            "uuid": uuid
        })
        # print(response)
        print("平台响应："+response.json()['msg'])
    except:
        print("登录失败")
        return False

    # 检测Http状态
    if response.json()['code'] != 200:
        print("登陆失败："+response.json()['msg'])
    else:
        try:
            print(username+"登陆成功，开始打卡")

            HEADERS['authorization'] = response.json()['token']
            response = requests.post(
                url=health_url, headers=HEADERS, json=get_health_param(COORD))
            # print(response)
        except:
            print(username+"打卡失败")
        HEADERS['authorization'] = ''

    # 解析结果
    try:
        if "已经打卡" in response.text:
            print(username+"🎉今天已经打过卡啦！")
            flag = True
        elif response.json()['code'] == 200:
            print(username+"🎉恭喜您打卡成功啦！")
            flag = True
        else:
            print(username+"打卡失败，平台响应：" + response.json())
    except:
        return False
    return flag


if __name__ == "__main__":
    count = 0
    failed = 0
    failed_username = ""

    # 循环打卡列表
    for i in array:
        if xiaobei_update(i[0], i[1]) == False:
            failed = failed+1
            failed_username = failed_username+str(i[0])+",\n"
        count = count+1
        sleep(1)

    if failed == 0:
        title="\n🎉恭喜您打卡成功啦！一共是"+str(count)+"人"
        message = yiyan()
    else:
        title = "\n😥共操作"+str(count)+"人,失败"+str(failed)+"人"
        message="失败账号：\n"+failed_username


    print(title)
    print(message)

    # 第三方推送
    if SENDKEY is None:
        SENDKEY = ''
    if WX_APP is None:
        WX_APP = ''
    if TG_BOT_TOKEN is None:
        TG_BOT_TOKEN = ''
    if TG_CHATID is None:
        TG_CHATID = ''

    title=title.replace("\n","")
    message=message.replace("\n","")

    if SENDKEY != '':
        try:
            sc_send(title, message)
        except:
            print("server酱发送失败")
    if TG_BOT_TOKEN and TG_CHATID != '':
        try:
            tg_send(title+message)
        except:
            print("电报机器人发送失败")
    if WX_APP != '':
        try:
            wxapp_notify(title+message)
        except:
            print("微信通知发送失败")
