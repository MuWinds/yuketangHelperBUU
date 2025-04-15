# -*- coding: utf-8 -*-
# version 4
# developed by zk chen
# developed by MuWinds
import random
import time
import requests
import re
import json
import threading

# 以下字段不用改，下面的代码也不用改动
user_id = ""
leaf_type = {"video": 0, "homework": 6, "exam": 5, "recommend": 3, "discussion": 4}


class videoHelper:
    def __init__(self, domain, cookies, user_id, university_id, learning_rate, header):

        self.domain = domain
        self.cookies = cookies
        self.user_id = user_id
        self.learning_rate = learning_rate
        self.university_id = university_id
        self.headers = header

    def one_video_watcher(self, video_id, video_name, cid, user_id, classroomid, skuid):
        video_id = str(video_id)
        classroomid = str(classroomid)
        url = "https://" + self.domain + "/video-log/heartbeat/"
        get_url = (
            "https://"
            + self.domain
            + "/video-log/get_video_watch_progress/?cid="
            + str(cid)
            + "&user_id="
            + user_id
            + "&classroom_id="
            + classroomid
            + "&video_type=video&vtype=rate&video_id="
            + str(video_id)
            + "&snapshot=1&term=latest&uv_id="
            + self.university_id
            + ""
        )
        progress = requests.get(url=get_url, headers=self.headers)
        if_completed = "0"
        try:
            if_completed = re.search(r'"completed":(.+?),', progress.text).group(1)
        except:
            pass
        if if_completed == "1":
            print(video_name + "已经学习完毕，跳过")
            return 1
        else:
            print(video_name + "，尚未学习，现在开始自动学习")
            time.sleep(2)

        # 默认为0（即还没开始看）
        video_frame = 0
        val = 0
        # 获取实际值（观看时长和完成率）
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
                        "pg": video_id
                        + "_"
                        + "".join(
                            random.sample("zyxwvutsrqponmlkjihgfedcba1234567890", 4)
                        ),
                        "sq": i + 1,
                        "t": "video",
                    }
                )
                video_frame += self.learning_rate
            data = {"heart_data": heart_data}
            r = requests.post(url=url, headers=self.headers, json=data, timeout=5)
            heart_data = []
            try:
                delay_time = (
                    re.search(r"Expected available in(.+?)second.", r.text)
                    .group(1)
                    .strip()
                )
                print("由于网络阻塞，万恶的雨课堂，要阻塞" + str(delay_time) + "秒")
                time.sleep(float(delay_time) + 0.5)
                print("恢复工作啦～～")
                submit_url = (
                    "https://"
                    + self.domain
                    + "/mooc-api/v1/lms/exercise/problem_apply/?term=latest&uv_id="
                    + self.university_id
                    + ""
                )
                r = requests.post(url=submit_url, headers=self.headers, data=data)
            except:
                pass
            try:
                progress = requests.get(url=get_url, headers=self.headers)
                res_rate = json.loads(progress.text)
                tmp_rate = res_rate["data"][video_id]["rate"]
                if tmp_rate is None:
                    return 0
                val = str(tmp_rate)
                print(
                    video_name
                    + "学习进度为：\t"
                    + str(format(float(val) * 100, ".2f"))
                    + "%"
                )
                time.sleep(2)
            except Exception as e:
                print(e.__str__())
                pass
        print("视频" + video_id + " " + video_name + "学习完成！")
        return 1

    def get_videos_ids(self, course_name, classroom_id, course_sign):
        get_homework_ids = (
            "https://"
            + self.domain
            + "/mooc-api/v1/lms/learn/course/chapter?cid="
            + str(classroom_id)
            + "&term=latest&uv_id="
            + self.university_id
            + "&sign="
            + course_sign
        )
        homework_ids_response = requests.get(url=get_homework_ids, headers=self.headers)
        homework_json = json.loads(homework_ids_response.text)
        homework_dic = {}
        try:
            for i in homework_json["data"]["course_chapter"]:
                for j in i["section_leaf_list"]:
                    if "leaf_list" in j:
                        for z in j["leaf_list"]:
                            if z["leaf_type"] == leaf_type["video"]:
                                homework_dic[z["id"]] = z["name"]
                    else:
                        if j["leaf_type"] == leaf_type["video"]:
                            # homework_ids.append(j["id"])
                            homework_dic[j["id"]] = j["name"]
            print(course_name + "共有" + str(len(homework_dic)) + "个作业喔！")
            return homework_dic
        except:
            print("fail while getting homework_ids!!! please re-run this program!")
            raise Exception(
                "fail while getting homework_ids!!! please re-run this program!"
            )

    def watch_videos(
        self, videos_id_name_dic, course_id, user_id, classroom_id, sku_id
    ):
        for one_video in videos_id_name_dic.items():
            self.one_video_watcher(
                one_video[0], one_video[1], course_id, user_id, classroom_id, sku_id
            )

    def multiple_watch_video(
        self,
        videos_id_name_dic,
        course_id,
        user_id,
        classroom_id,
        sku_id,
        num_workers=4,
    ):
        parts = list(videos_id_name_dic.items())
        threads = []
        for i in range(num_workers):
            part = parts[i::num_workers]
            thread = threading.Thread(
                target=self.watch_videos,
                args=(
                    {t[0]: t[1] for t in part[:]},
                    course_id,
                    user_id,
                    classroom_id,
                    sku_id,
                ),
            )
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
