# -*- coding: utf-8 -*-
# version 1
# developed by MuWinds
import requests
import time
import get_websockets
import json

def clear_cmdline_x10():                                    #调用此函数生成10行空格用于清屏
    for _ in range(10):
        print(" ")



def getUniversityId(domain):
    url = "https://"+domain+"/edu_admin/get_custom_university_info/?current=1&_=" + \
        str((round(time.time()*1000)))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
        'Content-Type': 'application/json',
    }
    response = requests.get(url=url, headers=headers).json()
    data = response['data']
    print(data['university_id'])
    return data['university_id']


def getWebSocketInfo(domain):
    ws = get_websockets.WebSocketQrcode()
    message = ws.run(domain)
    return message


def getCookies(domain):
    
    clear_cmdline_x10()
    print("+-----+-----+-----+-----+-----+-----+")
    print("                                     ")
    print("        是否使用已有cookies?          ")
    print("                                     ")
    print("           #cookies.txt#             ")
    print("                                     ")
    print("            [1]  使用                ")
    print("                                     ")
    print("            [0] 不使用               ")
    print("                                     ")
    print("                                     ")
    print("                                     ")
    print("                                     ")
    print("+-----+-----+-----+-----+-----+-----+")
    cookies_option = int(input("请输入选项(0-4):"))

    match cookies_option:
        case 0:
            is_cached = 0
        case 1:
            is_cached = 1
        case _:
            print("+-----+-----+-----+-----+-----+-----+")
            print("                                     ")
            print("         无效的选项！！！              ")
            print("    已缺省为不使用原有cookies          ")
            print("                                     ")
            print("+-----+-----+-----+-----+-----+-----+")

    if (is_cached == 1):
        filename = input("请输入cookies文件名:")
        ck_file = open(filename+".txt", "r")
        cookie = ck_file.read()
    else:
        university_id = getUniversityId(domain)
        login_message = getWebSocketInfo(domain)
        # message转json
        message = json.loads(login_message)
        auth_info = message['Auth']
        user_id = message['UserID']
        verify_url = "https://"+domain + \
            "/edu_admin/account/login/verify-origin-system-bind?term=latest&uv_id=" + \
            str(university_id)
        verify_header = {
            'referer': 'https://'+domain+'/pro/portal/home/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Cookie': 'university_id=3325;platform_id=3;xtbz=cloud;platform_type=1;',
            'Origin': 'https://'+domain,
            'Platform-Id': '3',
            'University-Id': str(university_id),
            'Terminal-Type': 'web',
            'X-Client': 'web',
            'X-Csrftoken': 'undefined',
            'Xtbz': 'cloud',
        }
        verify_form = {
            'auth': auth_info,
            'origin_user_id': str(user_id)
        }
        response = requests.post(
            verify_url, json=verify_form, headers=verify_header)
        cookie = response.headers.get('Set-Cookie')
        filename = input("请输入cookies文件名:")
        ck_write = open(filename+".txt", "w")
        ck_write.write(cookie)
    return cookie


def extract_specific_cookies(cookie_string):
    cookies = {}
    # 将cookie字符串分割成单独的cookie条目
    for cookie in cookie_string.split(','):
        # 进一步处理每个cookie，提取键和值
        key_value = cookie.split(';')[0].strip()  # 只获取键值对部分
        if '=' in key_value:
            key, value = key_value.split('=', 1)
            cookies[key] = value
    print(cookies.get('csrftoken'))
    print(cookies.get('sessionid'))
    # 返回特定的cookie
    return cookies.get('csrftoken'), cookies.get('sessionid')
