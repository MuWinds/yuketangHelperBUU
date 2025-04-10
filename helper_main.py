# -*- coding: utf-8 -*-
import requests
import re
import json
import get_info
from videoHelper import videoHelper
from homeworkHelper import homeworkHelper

domain = input("输入雨课堂域名：(BUU输入buu.yuketang.cn)")
cookies = get_info.getCookies(domain)
csrftoken, sessionid = get_info.extract_specific_cookies(cookies)  # 需改成自己的
university_id = get_info.getUniversityId(domain)  # 需改成自己的
university_id = str(university_id)  # 转成字符串
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    "Content-Type": "application/json",
    "Cookie": "csrftoken="
    + csrftoken
    + "; sessionid="
    + sessionid
    + "; university_id="
    + university_id
    + "; platform_id=3",
    "x-csrftoken": csrftoken,
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "university-id": university_id,
    "xtbz": "cloud",
}
if __name__ == "__main__":
    courses = []

    # 首先要获取用户的个人ID，即user_id,该值在查询用户的视频进度时需要使用
    user_id_url = "https://" + domain + "/edu_admin/check_user_session/"
    id_response = requests.get(url=user_id_url, headers=headers)
    try:
        user_id = re.search(r'"user_id":(.+?)}', id_response.text).group(1).strip()
    except:
        print("也许是网路问题，获取不了user_id,请试着重新运行")
        raise Exception(
            "也许是网路问题，获取不了user_id,请试着重新运行!!! please re-run this program!"
        )

    # 然后要获取教室id
    get_classroom_id = (
        "https://"
        + domain
        + "/mooc-api/v1/lms/user/user-courses/?status=1&page=1&no_page=1&term=latest&uv_id="
        + university_id
        + ""
    )
    submit_url = (
        "https://"
        + domain
        + "/mooc-api/v1/lms/exercise/problem_apply/?term=latest&uv_id="
        + university_id
        + ""
    )
    classroom_id_response = requests.get(url=get_classroom_id, headers=headers)
    try:
        for ins in json.loads(classroom_id_response.text)["data"]["product_list"]:
            courses.append(
                {
                    "course_name": ins["course_name"],
                    "classroom_id": ins["classroom_id"],
                    "course_sign": ins["course_sign"],
                    "sku_id": ins["sku_id"],
                    "course_id": ins["course_id"],
                }
            )
    except Exception as e:
        raise Exception(
            "fail while getting classroom_id!!! please re-run this program!"
        )

    # 显示用户提示
    for index, value in enumerate(courses):
        print("编号：" + str(index + 1) + " 课名：" + str(value["course_name"]))

    flag = True
    while flag:
        user_info_url = "https://" + domain + "/edu_admin/get_user_basic_info/"
        user_info_r = requests.get(url=user_info_url, headers=headers)
        try:
            user_info = json.loads(user_info_r.text)["data"]["user_info"]
            user_realname = user_info["name"]
            print("欢迎您，" + user_realname)
        except:
            print("也许是网路问题,获取不了user_info,请试着重新运行")
        number = input("你想刷哪门课呢?请输入编号。输入0表示全部课程都刷一遍\n")
        # 输入不合法则重新输入
        video_helper = videoHelper(domain, cookies, user_id, university_id, 12, headers)
        homework_helper = homeworkHelper(
            domain, cookies, user_id, university_id, headers
        )
        if not (number.isdigit()) or int(number) > len(courses):
            print("输入不合法！")
            continue
        elif int(number) == 0:
            flag = False  # 输入合法则不需要循环
            # 0 表示全部刷一遍
            for ins in courses:
                videos_id_name_dic = video_helper.get_videos_ids(
                    ins["course_name"], ins["classroom_id"], ins["course_sign"]
                )
                course_id = ins["course_id"]
                classroom_id = ins["classroom_id"]
                sku_id = ins["sku_id"]
                video_helper.multiple_watch_video(
                    videos_id_name_dic, course_id, user_id, classroom_id, sku_id
                )
            for ins in courses:
                homework_helper.do_homework(
                    ins["classroom_id"],
                    ins["course_sign"],
                    ins["course_name"],
                )
        else:
            flag = False  # 输入合法则不需要循环
            # 指定序号的课程刷一遍
            number = int(number) - 1
            videos_id_name_dic = video_helper.get_videos_ids(
                courses[number]["course_name"],
                courses[number]["classroom_id"],
                courses[number]["course_sign"],
            )
            ins = courses[number]
            course_id = ins["course_id"]
            classroom_id = ins["classroom_id"]
            sku_id = ins["sku_id"]
            video_helper.multiple_watch_video(
                videos_id_name_dic, course_id, user_id, classroom_id, sku_id
            )
            homework_helper.do_homework(
                courses[number]["classroom_id"],
                courses[number]["course_sign"],
                courses[number]["course_name"],
            )
        print("搞定啦")
