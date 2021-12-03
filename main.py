import base64
import json
import os
import random
import requests
import time

# 小北学生 账号密码
USERNAME = os.getenv("XB_USERNAME")
PASSWORD = os.getenv("XB_PASSWORD")
# 经纬度
LOCATION = os.getenv("XB_LOCATION")
# 位置，可选通过接口获取
COORD = os.getenv("XB_COORD")
# 邮件开关
# IS_EMAIL = os.getenv("XB_IS_EMAIL") #不要开关直接干掉
# 邮箱账号
EMAIL = os.getenv("XB_EMAIL")
# 企业微信应用
WX_APP = os.getenv("XB_WXAPP")
# 基本链接
BASE_URL = "https://xiaobei.yinghuaonline.com/xiaobei-api/"

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


# 判断环境变量里是否为空
if USERNAME is None or PASSWORD is None:
    USERNAME = str(input("请输入小北学生账号："))
    PASSWORD = str(input("请输入小北学生密码："))
    is_open()
    LOCATION = str(input("请将您所复制的经纬度粘贴到此处："))
    # COORD = str(input("请将您所在的区域【如：中国-云南省-昆明市-官渡区】："))
    EMAIL = input("接收邮箱账号,留空则不开启:")
    print("微信通知,开启需填写KEY，教程：https://ghurl.github.io/?130")
    WX_APP = input("微信通知密钥,留空则不开启:")
    PASSWORD = str(base64.b64encode(PASSWORD.encode()).decode())
else:
    PASSWORD = str(base64.b64encode(PASSWORD.encode()).decode())


def get_location():
    lc = LOCATION.split(',')
    location = lc[1] + ',' + lc[0]
    url = "https://api.xiaobaibk.com/api/location/?location=" + location
    try:
        result = requests.get(url).text
    except:
        print("获取地址失败！")
        wxapp_notify('😂由于获取位置信息失败打卡不成功，估计接口服务器崩了吧', '小北打卡失败')

    data = json.loads(result)
    if data['status'] == 0:
        province = data['result']['addressComponent']['province']
        city = data['result']['addressComponent']['city']
        district = data['result']['addressComponent']['district']
        return '中国-' + province + '-' + city + '-' + district
    else:
        print("位置获取失败,程序终止")
        os._exit(0)


def get_param(coord):
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


def send_mail(context):
    url = "https://api.xiaobaibk.com/api/mail/"
    js = {'mailto': EMAIL, 'content': context}
    # {"code":200,"msg":"\u606d\u559c\u60a8\u53d1\u9001\u6210\u529f\u4e86"}
    try:
        result = requests.post(url, js).text
    except:
        print("邮件发送不成功，估计邮件服务器崩了吧")
    type = json.loads(result)['code']
    if type == 200:
        print("邮件通知发送成功！")
    else:
        print("邮件通知发送失败，原因：" + json.loads(result)['msg'])


# 一言
def yiyan():
    try:
        txt = requests.get("https://api.xiaobaibk.com/api/yiyan.php").text
    except:
        txt = '随言获取失败，不清楚什么问题，问问作者吧'
    return txt


def wxapp_notify(content,title='小北成功打卡通知'):
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
        response = requests.post(url=url, headers=headers, data=json.dumps(payload), timeout=15).json()
    except:
        print("微信通知发送不成功！")
    accesstoken = response["access_token"]
    content = "打卡情况：[" + content + "]\n打卡位置：[" + COORD + "]\n打卡日期：[" + time.strftime("%Y-%m-%d") + "]\n随言：["+yiyan()+"]"
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
    response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()

    if response['errcode'] == 0:
        print('企业微信应用通知成功！')
    else:
        print('企业微信应用通知失败！')


if __name__ == '__main__':
    # Url
    # 滑动验证
    captcha = BASE_URL + 'captchaImage'
    # captcha = 'https://xiaobei.yinghuaonline.com/xiaobei-api/captchaImage'
    # https://xiaobei.yinghuaonline.com/xiaobei-api/captchaImage
    # 登录
    login = BASE_URL + 'login'
    # 打卡
    health = BASE_URL + 'student/health'

    # post method return 500 , So use the get method
    # data:   {"msg":"操作成功","img":"xxxxxx","code":200,"showCode":"NM6B","uuid":"4f72776b789b44d796722037ba7a1ff0"}
    try:
        response = requests.get(url=captcha, headers=HEADERS).text
    except:
        print("获取验证码出现错误！")
        wxapp_notify('😂估计小北服务器崩了或者在升级中，稍后运行脚本或者自行在软件打卡', '小北打卡失败')
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
    try:
        res = requests.post(url=login, headers=HEADERS, json=data).text
    except:
        print("用户登录不成功！")
        wxapp_notify('😂估计小北服务器崩了或者在升级中，稍后运行脚本或者自行在软件打卡', '小北打卡失败')
    code = json.loads(res)['code']
    msg = json.loads(res)['msg']


    if code != 200:
        print("Sorry! Login failed! Error：" + msg)
        # 发送邮件
        if EMAIL != '':
            send_mail("登录失败，失败原因：" + msg)
        if WX_APP != '':
            wxapp_notify("登录失败，失败原因：" + msg)
    else:
        print("登录成功！")

        # HEADERS.update({'authorization', token})
        # 换个方法
        HEADERS['authorization'] = json.loads(res)['token']

        # 获取位置
        if COORD is None or COORD == '':
            COORD = get_location()
        else:
            pass

        health_param = None

        print(COORD)
        if LOCATION is not None and COORD is not None:
            health_param = get_param(COORD)
        else:
            print("必要参数为空！")

        try:
            respond = requests.post(url=health, headers=HEADERS, json=health_param).text
        except:
            print("打卡失败！")
            wxapp_notify('😩可以正常登录但是遇到异常，原因不明，请自行打卡', '小北打卡失败')
        # error return {'msg': None, 'code': 500}
        # succeed return {'msg': '操作成功', 'code': 200}
        status = json.loads(respond)['code']
        if status == 200:
            print("恭喜您打卡成功啦！")
            if EMAIL != '':
                send_mail("打卡成功啦🎉")
            if WX_APP != '':
                wxapp_notify("打卡成功啦🎉")
        else:
            print("Error：" + json.loads(respond)['msg'])
            if EMAIL != 'yes':
                send_mail("🙁抱歉打卡失败了，原因未知，请自行手动打卡，谢谢")
            if WX_APP != '':
                wxapp_notify("🙁抱歉打卡失败了，请自行手动打卡，谢谢--->失败原因:"+json.loads(respond)['msg'], '打卡失败')
