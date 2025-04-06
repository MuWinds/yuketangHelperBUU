from openai import OpenAI
import json


class OpenAI_ask:
    def __init__(self):
        self.config = json.load(open('config.json', 'r', encoding='utf-8'))
        self.base_url = self.config['base_url']
        self.api_key = self.config['key']
        self.model = self.config['model']

    def get_answer(self, problem):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "回答下面的问题,直接返回答案对应选项的字母,不要回复多余内容,如果不知道答案,请直接回答C,多选题回答格式是每个选项之间用一个半角逗号和一个空格分开，判断题只用返回true或false，不用回复标点符号。"},
                {"role": "user", "content": problem},
            ],
            temperature=0.7,
        )
        if (len(response.choices[0].message.content) == 1):
            result = response.choices[0].message.content
        else:
            result = [item.strip()
                      for item in response.choices[0].message.content.split(",")]
        return result
