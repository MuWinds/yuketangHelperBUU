# -*- coding: utf-8 -*-
# version:5.0
# developed by zk chen and MR.Li
# develpoed by MuWinds
# V3版本仅能刷项目管理概论作业题
# V4版本由李同学改良，可以刷用户名下所有的课程的线上作业
# V5版本旨在跨学院使用，在微电子学院网课中发现了填空题类型，因此兼容了填空题，另外增加了交互，可以选择想刷哪个课程
# MuWinds:雨课堂题目进行解密，AI 回答，自动提交
import requests
from decrypt_problem import Decrypt_problem
import json
import re
import time
from openai_ask import OpenAI_ask


class homeworkHelper:
    def __init__(self, domain, cookies, user_id, university_id, header):
        self.domain = domain
        self.cookies = cookies
        self.user_id = user_id
        self.university_id = university_id
        self.headers = header
        self.leaf_type = {
            "video": 0,
            "homework": 6,
            "exam": 5,
            "recommend": 3,
            "discussion": 4
        }

    def do_homework(self, classroom_id, course_sign, course_name):
        # 获取每个作业的id
        submit_url = "https://"+self.domain + \
            "/mooc-api/v1/lms/exercise/problem_apply/?term=latest&uv_id=" + self.university_id + ""
        get_homework_ids = "https://"+self.domain+"/mooc-api/v1/lms/learn/course/chapter?cid=" + \
            str(classroom_id)+"&term=latest&uv_id=" + \
            self.university_id+"&sign="+course_sign
        homework_ids_response = requests.get(
            url=get_homework_ids, headers=self.headers)
        homework_json = json.loads(homework_ids_response.text)
        homework_ids = []
        try:
            for i in homework_json["data"]["course_chapter"]:
                for j in i["section_leaf_list"]:
                    if "leaf_list" in j:
                        for z in j["leaf_list"]:
                            # print(z['leaf_type'], z['name'], z['id'])
                            if z['leaf_type'] == self.leaf_type["homework"]:
                                print(z['name'], z['leaf_type'],
                                      self.leaf_type["homework"], z['id'])
                                homework_ids.append(z["id"])
                    else:
                        if j['leaf_type'] == self.leaf_type["homework"]:
                            homework_ids.append(j["id"])
            print("| INFO | " + course_name+"共有"+str(len(homework_ids))+"个作业喔！")
        except:
            print("fail while getting homework_ids!!! please re-run this program!")
            raise Exception(
                "fail while getting homework_ids!!! please re-run this program!")

        # finally, we have all the data needed
        for homework in homework_ids:
            get_leaf_type_id_url = "https://"+self.domain+"/mooc-api/v1/lms/learn/leaf_info/" + \
                str(classroom_id)+"/"+str(homework)+"/?term=latest&uv_id=3078"
            leaf_response = requests.get(
                url=get_leaf_type_id_url, headers=self.headers)
            try:
                leaf_id = json.loads(leaf_response.text)[
                    "data"]["content_info"]["leaf_type_id"]
            except:
                continue
            problem_url = "https://"+self.domain+"/mooc-api/v1/lms/exercise/get_exercise_list/" + \
                str(leaf_id)+"/?term=latest&uv_id="+self.university_id
            id_response = requests.get(url=problem_url, headers=self.headers)
            dictionary = json.loads(id_response.text)
            font_ttf = dictionary['data']['font']
            decrypt = Decrypt_problem(header=self.headers)
            decrypted_str = decrypt.get_encrypt_string(
                id_response.text, font_ttf)
            dictionary = json.loads(decrypted_str)
            # 提取题目并格式化为字典结构
            questions_dict = {}  # 改用字典存储
            for problem in dictionary["data"]["problems"]:
                problem_id = problem["problem_id"]  # 提取题目ID作为键
                content = problem["content"]
                if problem['user']['my_count'] >= problem['user']['count']:
                    print("| WARN | " +"该问题已经超过做题上限了，所以不得不跳过啦~")
                    continue
                options = [
                    f"{opt['key']}. {opt['value']}" for opt in content["Options"]]
                # 构建值字符串（不再需要包含ID）
                question_str = f"[{content['TypeText']}]{content['Body']} 选项：[{', '.join(options)}]"
                questions_dict[problem_id] = question_str  # 存入字典

            # 回答问题
            for pid, q in questions_dict.items():
                print("| INFO | " + f"问题: {q}")

                openai_solve = OpenAI_ask()
                answer = openai_solve.get_answer(q)
                submit_dict = {
                    "classroom_id": classroom_id,
                    "problem_id": pid,
                    "answer": answer
                }
                submit_json_data = json.dumps(submit_dict)
                print(submit_json_data)
                retries = 0
                while retries < 3:  # 添加重试循环，限制最大重试次数
                    try:
                        response = requests.post(
                            url=submit_url,
                            headers=self.headers,
                            data=submit_json_data,
                            timeout=(3, 10)
                        )
                        response_json = json.loads(response.text)  # 解析 JSON 响应

                        if 'detail' in response_json and "Expected available in" in response_json['detail']:
                            delay_match = re.search(
                                r'Expected available in (\d+\.?\d*) seconds\.', response_json['detail'])
                            if delay_match:
                                delay_time = float(delay_match.group(1))
                                print("| WARN | " +f"由于网络阻塞，万恶的雨课堂，要阻塞 {delay_time} 秒")
                                time.sleep(delay_time + 1)  # 等待指定时间 + 1 秒，更保险
                                retries += 1
                                print("| WARN | " +f"等待结束，进行第 {retries} 次重试...")
                                continue  # 继续下一次循环，即重试提交

                        print(response.text)  # 打印正常响应
                        break  # 提交成功，跳出重试循环

                    except requests.exceptions.Timeout as e:
                        print("| WARN | " +f"请求超时，第{retries+1}次重试...")
                        retries += 1
                        time.sleep(2 ** retries)  # 指数退避
                    except requests.exceptions.RequestException as e:  # 捕获其他请求异常
                        print("| ERROR |" +f"请求异常: {str(e)}")
                        break  # 遇到其他请求异常，跳出重试循环，避免无限重试
            print("| INFO | " + dictionary["data"]["name"] + "已经完成!")
