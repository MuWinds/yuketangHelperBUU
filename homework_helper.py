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
from fontTools.pens.ttGlyphPen import TTGlyphPen
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

def hash_glyph_commands(commands):
    """与生成映射文件时相同的哈希生成函数"""
    command_str = json.dumps(commands, sort_keys=True)
    return hashlib.sha1(command_str.encode()).hexdigest()

def decrypt_font(obfuscated_font_path, mapping_file_path):
    # 加载混淆字体
    font_res = requests.get(url = obfuscated_font_path,headers=headers)
    font_data = BytesIO(font_res.content)
    obfuscated_font = TTFont(font_data)
    
    # 构建字形名称到Unicode的反向映射
    cmap = obfuscated_font.getBestCmap()
    glyph_unicodes = {}
    for code, name in cmap.items():
        glyph_unicodes.setdefault(name, []).append(code)
    
    # 加载原始映射表
    with open(mapping_file_path, 'r', encoding='utf-8') as f:
        original_glyph_to_uni = json.load(f)
    
    obfuscated_to_original = {}
    
    # 遍历所有混淆字形
    for glyph_name in obfuscated_font.getGlyphOrder():
        # 获取对应的Unicode码点（可能有多个，取第一个）
        unicodes = glyph_unicodes.get(glyph_name, [])
        if not unicodes:
            continue
        unicode_t = unicodes[0]  # 假设取第一个码点
        
        glyph = obfuscated_font['glyf'][glyph_name]
        commands = []
        
        # 构造路径命令（与生成映射文件时相同的逻辑）
        if glyph.numberOfContours > 0:
            # 简单字形
            end_pts = glyph.endPtsOfContours
            coords = glyph.coordinates
            commands = [f"CONTOUR_END:{end_pts}", f"COORDS:{coords}"]
        elif glyph.isComposite():
            # 复合字形
            components = [f"{comp.glyphName}({comp.x},{comp.y})" 
                          for comp in glyph.components]
            commands = ["COMPOSITE"] + components
        
        # 生成哈希
        glyph_hash = hash_glyph_commands(commands)
        
        # 查找映射表
        if glyph_hash in original_glyph_to_uni:
            unicode_s = original_glyph_to_uni[glyph_hash]
            obfuscated_to_original[unicode_t] = unicode_s
    
    return obfuscated_to_original

def get_encrypt_string(s, ttf_path):
    # 生成解密映射表
    decryption_map = decrypt_font(ttf_path, "mapping_file.json")
    
    # 解析原始字符串为Python对象
    data = json.loads(s)
    
    # 定义递归替换函数
    def replace_encrypted_text(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = replace_encrypted_text(value)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = replace_encrypted_text(obj[i])
        elif isinstance(obj, str):
            # 使用正则表达式进行替换
            def decrypt_match(match):
                encrypted_str = match.group(1)
                decrypted_chars = [
                    chr(decryption_map.get(ord(c), ord(c)))
                    for c in encrypted_str
                ]
                return ''.join(decrypted_chars)
            
            # 替换所有加密标签内容
            obj = re.sub(
                r'<span class="xuetangx-com-encrypted-font">(.*?)</span>',
                decrypt_match,
                obj
            )
        return obj
    
    # 执行递归替换
    modified_data = replace_encrypted_text(data)
    
    # 将修改后的数据转换回JSON字符串
    modified_s = json.dumps(modified_data, ensure_ascii=False)
    
    return format_string(modified_s)

def format_string(src):
    #格式化字符串
    src = str(src) # Convert input to string

    if "img" in src or "iframe" in src:
        pass # Bypass HTMLDecode if "img" or "iframe" is present
    else:
        src = unescape(src) # Decode HTML entities

    # Convert full-width characters to half-width characters
    src = re.sub(r'[\uff01-\uff5e]', lambda char: chr(ord(char.group(0)) - 65248), src)

    # Replace multiple spaces with single space
    src = re.sub(r'\s+', ' ', src)

    # Replace full-width and curly quotes with standard quotes
    src = re.sub(r'[“”]', '"', src)
    src = re.sub(r'[‘’]', "'", src)

    # Replace full-width period with standard period
    src = src.replace('。', '.')

    # Remove trailing punctuation marks: , . ? : ! ;
    src = re.sub(r'[,.?:!;]$', '', src)

    src = src.strip() # Trim leading/trailing whitespace

    return src

def do_homework(submit_url, classroom_id, course_sign, course_name):
    # 获取每个作业的id
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
        print(dictionary)
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
