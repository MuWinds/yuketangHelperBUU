# -*- coding: utf-8 -*-
# version 1
# developed by MuWinds
import requests
import time
import get_websockets
import json
import cmdline_menu

#初始化cmdline_menu
menuType = "medium"
borderStyle = "dashed"
cmdline_menu.initialize_menu_type(menuType , borderStyle)



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
    
    cmdline_menu.clear_cmdline_x10()
    cmdline_menu.clear_cmdline_x10()
    cmdline_menu.drawBorder(menuType , borderStyle)
    cmdline_menu.singlespace()
    cmdline_menu.singlespace()
    cmdline_menu.raw_text("是否使用已有cookies?")
    cmdline_menu.singlespace()
    cmdline_menu.raw_text("#cookies.txt#")
    cmdline_menu.singlespace()
    cmdline_menu.create_option("1","使用")
    cmdline_menu.singlespace()
    cmdline_menu.create_option("0","不使用")
    cmdline_menu.singlespace()
    cmdline_menu.singlespace()
    cmdline_menu.singlespace()
    cmdline_menu.singlespace()
    cmdline_menu.drawBorder(menuType , borderStyle)
    print("请输入选项(0-1):")
    cookies_option = cmdline_menu.read_selection()

    match cookies_option:
        case 0:
            is_cached = 0
        case 1:
            is_cached = 1
        case _:
            cmdline_menu.clear_cmdline_x10()
            cmdline_menu.clear_cmdline_x10()
            cmdline_menu.drawBorder(menuType , borderStyle)
            cmdline_menu.singlespace()
            cmdline_menu.raw_text("无效的选项！！！")
            cmdline_menu.raw_text("已缺省为不使用原有cookies")
            cmdline_menu.singlespace()
            cmdline_menu.drawBorder(menuType , borderStyle)

    if (is_cached == "1"):
        cmdline_menu.clear_cmdline_x10()
        cmdline_menu.clear_cmdline_x10()
        cmdline_menu.drawBorder(menuType , borderStyle)
        cmdline_menu.singlespace()
        cmdline_menu.singlespace()
        cmdline_menu.raw_text("请输入cookies文件名")
        cmdline_menu.singlespace()
        cmdline_menu.singlespace()
        cmdline_menu.create_option("1","缺省cookies.txt")
        cmdline_menu.create_option("0","手动输入")
        cmdline_menu.singlespace()
        cmdline_menu.singlespace()
        cmdline_menu.drawBorder(menuType , borderStyle)
        cookies_option = cmdline_menu.read_selection()
        match cookies_option:
            case 1:
                filename = "cookies"
            case 0:
                cmdline_menu.clear_cmdline_x10()
                cmdline_menu.clear_cmdline_x10()
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
        cmdline_menu.clear_cmdline_x10()
        cmdline_menu.clear_cmdline_x10()
        cmdline_menu.drawBorder(menuType , borderStyle)
        cmdline_menu.singlespace()
        cmdline_menu.singlespace()
        cmdline_menu.raw_text("请输入cookies文件名")
        cmdline_menu.singlespace()
        cmdline_menu.singlespace()
        cmdline_menu.create_option("1","缺省cookies.txt")
        cmdline_menu.create_option("0","手动输入")
        cmdline_menu.singlespace()
        cmdline_menu.singlespace()
        cmdline_menu.drawBorder(menuType , borderStyle)
        cookies_option = cmdline_menu.read_selection()
        match cookies_option:
            case 1:
                filename = "cookies"
                cmdline_menu.clear_cmdline_x10()
                cmdline_menu.clear_cmdline_x10()
                cmdline_menu.drawBorder(menuType , borderStyle)
                cmdline_menu.singlespace()
                cmdline_menu.singlespace()
                cmdline_menu.raw_text("cookies.txt已覆盖")
                cmdline_menu.singlespace()
                cmdline_menu.singlespace()
                cmdline_menu.singlespace()
                cmdline_menu.singlespace()
                cmdline_menu.drawBorder(menuType , borderStyle)
            case 0:
                cmdline_menu.clear_cmdline_x10()
                cmdline_menu.clear_cmdline_x10()
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
