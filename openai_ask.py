from openai import OpenAI
import json


class OpenAI_ask:
    def __init__(self):
        self.config = json.load(open("config.json", "r", encoding="utf-8"))
        self.base_url = self.config["base_url"]
        self.api_key = self.config["key"]
        self.system_prompt = self.config["system_prompt"]
        self.model = self.config["model"]

    def get_answer(self, problem,problem_type='Choice'):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {"role": "user", "content": problem},
            ],
            temperature=0.7,
        )
        if len(response.choices[0].message.content) == 1 or problem_type == 'FillBlank':
            result = response.choices[0].message.content
        else:
            result = [
                item.strip() for item in response.choices[0].message.content.split(",")
            ]
        return result
