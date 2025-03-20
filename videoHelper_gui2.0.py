# -*- coding: utf-8 -*-
# version 4
# developed by zk chen
# developed by MuWinds
import random
import time
import requests
import re
import json
import get_info
import threading
from gooey import Gooey, GooeyParser

@Gooey(program_name="雨课堂视频助手", 
       progress_regex=r"^progress: (\d+)%$", 
       progress_expr="x[0]")
def main():
    parser = GooeyParser(description="自动刷雨课堂视频")
    parser.add_argument('domain', metavar='雨课堂域名(需改成自己学校的)', help='例如: buu.yuketang.cn', default='buu.yuketang.cn')
    parser.add_argument('cookies',metavar='Cookie',help='输入自己的Cookie',default='1')
    parser.add_argument('n',metavar='不要动这个',help='不要动这个',default='0')
    args = parser.parse_args()
    
    domain = args.domain
    cookies = args.cookies
    csrftoken, sessionid = get_info.extract_specific_cookies(cookies)
    university_id = get_info.getUniversityId(domain)
    university_id = str(university_id)
    learning_rate = 20

    user_id = ""

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

    def one_video_watcher(video_id, video_name, cid, user_id, classroomid, skuid):
        video_id = str(video_id)
        classroomid = str(classroomid)
        url = "https://"+domain + "/video-log/heartbeat/"
        get_url = "https://"+domain + "/video-log/get_video_watch_progress/?cid=" + str(
            cid) + "&user_id=" + user_id + "&classroom_id=" + classroomid + "&video_type=video&vtype=rate&video_id=" + str(
            video_id) + "&snapshot=1&term=latest&uv_id=" + university_id + ""
        progress = requests.get(url=get_url, headers=headers)
        if_completed = '0'
        try:
            if_completed = re.search(r'"completed":(.+?),', progress.text).group(1)
        except:
            pass
        if if_completed == '1':
            print(video_name + "已经学习完毕，跳过")
            return 1
        else:
            print(video_name + "，尚未学习，现在开始自动学习")
            time.sleep(2)

        video_frame = 0
        val = 0
        try:
            res_rate = json.loads(progress.text)
            tmp_rate = res_rate["data"][video_id]["rate"]
            if tmp_rate is None:
                return 0
            val = tmp_rate
            video_frame = res_rate["data"][video_id]["watch_length"]
        except Exception as e:
            print(e.__str__())

        t = time.time()
        timstap = int(round(t * 1000))
        heart_data = []
        while float(val) <= 0.95:
            for i in range(3):
                heart_data.append(
                    {
                        "i": 5,
                        "et": "loadeddata",
                        "p": "web",
                        "n": "ali-cdn.xuetangx.com",
                        "lob": "cloud4",
                        "cp": video_frame,
                        "fp": 0,
                        "tp": 0,
                        "sp": 2,
                        "ts": str(timstap),
                        "u": int(user_id),
                        "uip": "",
                        "c": cid,
                        "v": int(video_id),
                        "skuid": skuid,
                        "classroomid": classroomid,
                        "cc": video_id,
                        "d": 4976.5,
                        "pg": video_id + "_" + ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba1234567890', 4)),
                        "sq": i,
                        "t": "video"
                    }
                )
                video_frame += learning_rate
            data = {"heart_data": heart_data}
            r = requests.post(url=url, headers=headers, json=data)
            heart_data = []
            try:
                delay_time = re.search(r'Expected available in(.+?)second.', r.text).group(1).strip()
                print("由于网络阻塞，万恶的雨课堂，要阻塞" + str(delay_time) + "秒")
                time.sleep(float(delay_time) + 0.5)
                print("恢复工作啦～～")
                r = requests.post(url=submit_url, headers=headers, data=data)
            except:
                pass
            try:
                progress = requests.get(url=get_url, headers=headers)
                res_rate = json.loads(progress.text)
                tmp_rate = res_rate["data"][video_id]["rate"]
                if tmp_rate is None:
                    return 0
                val = str(tmp_rate)
                print(video_name+"学习进度为：\t" + str(format(float(val)* 100,'.2f') ) + "%")
                time.sleep(2)
            except Exception as e:
                print(e.__str__())
                pass
        print("视频" + video_id + " " + video_name + "学习完成！")
        return 1

    def get_videos_ids(course_name, classroom_id, course_sign):
        get_homework_ids = "https://"+domain + "/mooc-api/v1/lms/learn/course/chapter?cid=" + str(
            classroom_id) + "&term=latest&uv_id=" + university_id + "&sign=" + course_sign
        homework_ids_response = requests.get(url=get_homework_ids, headers=headers)
        
        if homework_ids_response.status_code != 200:
            print(f"请求失败，状态码：{homework_ids_response.status_code}")
            raise Exception("请求失败，检查网络或认证信息")
        
        if not homework_ids_response.text:
            print("响应内容为空!")
            raise Exception("响应内容为空，检查请求参数")
        
        try:
            homework_json = json.loads(homework_ids_response.text)
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            print(f"响应内容: {homework_ids_response.text}")
            raise Exception("JSON 解析失败，请检查响应内容")
        
        homework_dic = {}
        try:
            for i in homework_json["data"]["course_chapter"]:
                for j in i["section_leaf_list"]:
                    if "leaf_list" in j:
                        for z in j["leaf_list"]:
                            if z['leaf_type'] == leaf_type["video"]:
                                homework_dic[z["id"]] = z["name"]
                    else:
                        if j['leaf_type'] == leaf_type["video"]:
                            homework_dic[j["id"]] = j["name"]
            print(course_name + "共有" + str(len(homework_dic)) + "个作业喔！")
            return homework_dic
        except Exception as e:
            print("获取作业 ID 失败: " + str(e))
            raise Exception("获取作业 ID 失败，请重新运行程序")

    def watch_videos(videos_id_name_dic, course_id, user_id, classroom_id, sku_id):
        for one_video in videos_id_name_dic.items():
            one_video_watcher(one_video[0], one_video[1], course_id, user_id, classroom_id, sku_id)

    def multiple_watch_video(videos_id_name_dic, course_id, user_id, classroom_id, sku_id, num_workers=4):
        parts = list(videos_id_name_dic.items())
        threads = []
        for i in range(num_workers):
            part = parts[i::num_workers]
            thread = threading.Thread(target=watch_videos, args=({t[0]: t[1] for t in part[:]}, course_id, user_id, classroom_id, sku_id))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    if __name__ == "__main__":
        courses = []

        user_id_url = "https://"+domain + "/edu_admin/check_user_session/"
        id_response = requests.get(url=user_id_url, headers=headers)
        try:
            user_id = re.search(r'"user_id":(.+?)}', id_response.text).group(1).strip()
        except:
            print("也许是网路问题，获取不了user_id,请试着重新运行")
            raise Exception("也许是网路问题，获取不了user_id,请试着重新运行!!! please re-run this program!")

        get_classroom_id = "https://"+domain + "/mooc-api/v1/lms/user/user-courses/?status=1&page=1&no_page=1&term=latest&uv_id=" + university_id + ""
        submit_url = "https://"+domain + "/mooc-api/v1/lms/exercise/problem_apply/?term=latest&uv_id=" + university_id + ""
        classroom_id_response = requests.get(url=get_classroom_id, headers=headers)
        try:
            for ins in json.loads(classroom_id_response.text)["data"]["product_list"]:
                courses.append({
                    "course_name": ins["course_name"],
                    "classroom_id": ins["classroom_id"],
                    "course_sign": ins["course_sign"],
                    "sku_id": ins["sku_id"],
                    "course_id": ins["course_id"]
                })
        except Exception as e:
            print("fail while getting classroom_id!!! please re-run this program!")
            raise Exception("fail while getting classroom_id!!! please re-run this program!")

        for index, value in enumerate(courses):
            print("编号：" + str(index + 1) + " 课名：" + str(value["course_name"]))

        flag = True
        while(flag):
            number = args.n
            if not (number.isdigit()) or int(number) > len(courses):
                print("输入不合法！")
                continue
            elif int(number) == 0:
                flag = False
                for ins in courses:
                    videos_id_name_dic = get_videos_ids(ins["course_name"], ins["classroom_id"], ins["course_sign"])
                    course_id = ins["course_id"]
                    classroom_id = ins["classroom_id"]
                    sku_id = ins["sku_id"]
                    multiple_watch_video(videos_id_name_dic, course_id, user_id, classroom_id, sku_id)
            else:
                flag = False
                number = int(number) - 1
                videos_id_name_dic = get_videos_ids(courses[number]["course_name"], courses[number]["classroom_id"],
                                                    courses[number]["course_sign"])
                ins = courses[number]
                course_id = ins["course_id"]
                classroom_id = ins["classroom_id"]
                sku_id = ins["sku_id"]
                multiple_watch_video(videos_id_name_dic, course_id, user_id, classroom_id, sku_id)
            print("搞定啦")

if __name__ == "__main__":
    main()