from openai import OpenAI
import json
import re

class OpenAI_ask:
    def __init__(self):
        self.config = json.load(open("config.json", "r", encoding="utf-8"))
        self.base_url = self.config["base_url"]
        self.api_key = self.config["key"]
        self.system_prompt = self.config["system_prompt"]
        self.model = self.config["model"]

    def get_answer(self, problem,problem_type='Choice',leaf_type = 6):
        if leaf_type == 4 :
            system_prompt = "以一个大学生/研究生的视角，回答下面的讨论问题,整体内容300字左右，注意不要直接体现大学生/" \
                            "研究生字眼，内容详略得当且连贯，不官方死板，不举太尴尬的例子。" \
                            "直接回答答案，不要用markdown形式，不要有如'#','$'，'*'等符号,不要有多余的空行。"
        else:
            system_prompt = self.system_prompt
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": problem},
            ],
            temperature=0.7,
        )
        # 1. 获取模型返回的原始全文
        full_content = response.choices[0].message.content

        # 2. 使用正则剔除 <think>...</think> 及其包含的所有内容
        # flags=re.DOTALL 确保可以匹配跨行的思考过程
        nothink_content = re.sub(r'<think>.*?</think>', '', full_content, flags=re.DOTALL).strip()

        # 3. 基于清洗后的内容进行原有逻辑判断
        if len(nothink_content) == 1 or problem_type == 'FillBlank' or leaf_type == 4:
            result = nothink_content
        else:
            result = [
                item.strip() for item in nothink_content.split(",") if item.strip()
            ]
        #print(f"result:\n{result}\n")
        return result
