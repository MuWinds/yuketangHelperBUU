# -*- coding: utf-8 -*-
# version:5.0
# developed by zk chen and MR.Li
# V3版本仅能刷项目管理概论作业题
# V4版本由李同学改良，可以刷用户名下所有的课程的线上作业
# V5版本旨在跨学院使用，在微电子学院网课中发现了填空题类型，因此兼容了填空题，另外增加了交互，可以选择想刷哪个课程
import hashlib
import requests
from fontTools.ttLib import TTFont
from fontTools.pens.hashPointPen import HashPointPen
from html import unescape
import re
import json
from io import BytesIO
import get_info

domain = input('输入雨课堂域名：(BUU输入buu.yuketang.cn)')
cookies = get_info.getCookies(domain)
csrftoken,sessionid = get_info.extract_specific_cookies(cookies);  # 需改成自己的
university_id = get_info.getUniversityId(domain)  # 需改成自己的
university_id = str(university_id)#转成字符串csrftoken = "yours" #需改成自己的

# 会自动跳过已经完成的题目，无须担心，如果运行一遍后，仍有遗漏，再次运行即可。
# 因为作业答案在网页接口中返回了，因此本脚本才能自动答题
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': 'csrftoken=' + csrftoken + '; sessionid=' + sessionid + '; university_id=' + str(university_id) + '; platform_id=3',
    'x-csrftoken': csrftoken,
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'university-id': university_id,
    'xtbz': 'cloud'
}

leaf_type = {
    "video": 0,
    "homework": 6,
    "exam": 5,
    "recommend": 3,
    "discussion": 4
}

def get_encrypt_string(s, ttf):
    # 匹配加密部分
    # 假设data_str是用户提供的原始JSON字符串
    # 解析为字典
    data_dict = json.loads(s)
    res = requests.get(ttf,headers=headers)
    # 递归遍历字典中的所有字符串值
    def find_encrypted_text(obj):
        results = []
        if isinstance(obj, dict):
            for value in obj.values():
                results.extend(find_encrypted_text(value))
        elif isinstance(obj, list):
            for item in obj:
                results.extend(find_encrypted_text(item))
        elif isinstance(obj, str):
            # 应用正则表达式
            pattern = r'<span class="xuetangx-com-encrypted-font">(.*?)</span>'
            matches = re.findall(pattern, obj)
            results.extend(matches)
        return results
    matches = find_encrypted_text(data_dict)
    for enc_str in matches:
        dec_str = decrypt_text(enc_str,res.content,"mapping_file.json")
        s = s.replace(f'<span class="xuetangx-com-encrypted-font">{enc_str}</span>', ''.join(dec_str))
        print(dec_str)
        print(enc)
    return format_string(s)

def do_homework(submit_url, classroom_id, course_sign, course_name):
    # second, need to get homework ids
    get_homework_ids = "https://"+domain+"/mooc-api/v1/lms/learn/course/chapter?cid="+str(classroom_id)+"&term=latest&uv_id="+university_id+"&sign="+course_sign
    homework_ids_response = requests.get(url=get_homework_ids, headers=headers)
    print(homework_ids_response.text)
    homework_json = json.loads(homework_ids_response.text)
    homework_ids = []
    try:
        for i in homework_json["data"]["course_chapter"]:
            for j in i["section_leaf_list"]:
                if "leaf_list" in j:
                    for z in j["leaf_list"]:
                        #print(z['leaf_type'], z['name'], z['id'])
                        if z['leaf_type'] == leaf_type["homework"]:
                            print(z['name'], z['leaf_type'], leaf_type["homework"], z['id'])
                            homework_ids.append(z["id"])
                else:
                    if j['leaf_type'] == leaf_type["homework"]:
                        homework_ids.append(j["id"])
        print(course_name+"共有"+str(len(homework_ids))+"个作业喔！")
    except:
        print("fail while getting homework_ids!!! please re-run this program!")
        raise Exception("fail while getting homework_ids!!! please re-run this program!")

    # finally, we have all the data needed
    for homework in homework_ids:
        get_leaf_type_id_url = "https://"+domain+"/mooc-api/v1/lms/learn/leaf_info/"+str(classroom_id)+"/"+str(homework)+"/?term=latest&uv_id=3078"
        leaf_response = requests.get(url=get_leaf_type_id_url, headers=headers)
        try:
            leaf_id = json.loads(leaf_response.text)["data"]["content_info"]["leaf_type_id"]
        except:
            continue
        problem_url = "https://"+domain+"/mooc-api/v1/lms/exercise/get_exercise_list/"+str(leaf_id)+"/?term=latest&uv_id="+university_id
        id_response = requests.get(url=problem_url, headers=headers)
        dictionary = json.loads(id_response.text)
        font_ttf = dictionary['data']['font']
        decrypted_str = get_encrypt_string(id_response.text,font_ttf)
        dictionary = json.loads(decrypted_str)
        # print(dictionary)
            # try:
            #     delay_time = re.search(r'Expected available in(.+?)second.',response.text).group(1).strip()
            #     print("由于网络阻塞，万恶的雨课堂，要阻塞" +str(delay_time)+"秒")
            #     time.sleep(float(delay_time)+0.5)
            #     print("恢复工作啦～～")
            #     response = requests.post(url=submit_url, headers=headers, data=json.dumps(submit_json_data))
            # except:
            #     pass
            # time.sleep(0.5)
        # print(dictionary["data"]["name"] + "已经完成!")

if __name__ == "__main__":
    your_courses = []
    course = {}

    # first, need to get classroom_id
    get_classroom_id = "https://"+domain + "/mooc-api/v1/lms/user/user-courses/?status=1&page=1&no_page=1&term=latest&uv_id=" + university_id + ""    
    submit_url = "https://"+domain+"/mooc-api/v1/lms/exercise/problem_apply/?term=latest&uv_id="+university_id+""
    classroom_id_response = requests.get(url=get_classroom_id, headers=headers)
    try:
        for ins in json.loads(classroom_id_response.text)["data"]["product_list"]:
            your_courses.append({
                "course_name": ins["course_name"],
                "classroom_id": ins["classroom_id"],
                "course_sign": ins["course_sign"],
                "sku_id": ins["sku_id"],
                "course_id": ins["course_id"]
            })
    except Exception as e:
        print("fail while getting classroom_id!!! please re-run this program!")
        raise Exception("fail while getting classroom_id!!! please re-run this program!")
    for index, value in enumerate(your_courses):
        print("编号："+str(index+1)+" 课名："+str(value["course_name"]))
    number = input("你想刷哪门课呢?请输入编号。输入0表示全部课程都刷一遍\n")
    if int(number)==0:
        for ins in your_courses:
            do_homework(submit_url, ins["classroom_id"], ins["course_sign"], ins["course_name"])
    else:
        number = int(number)-1
        do_homework(submit_url, your_courses[number]["classroom_id"], your_courses[number]["course_sign"], your_courses[number]["course_name"])
