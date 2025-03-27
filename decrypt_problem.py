import re
import hashlib
import json
import requests
from io import BytesIO
from fontTools.ttLib import TTFont
from bs4 import BeautifulSoup


class Decrypt_problem:
    def __init__(self, header):
        self.header = header

    @staticmethod
    def hash_glyph_commands(commands):
        """与生成映射文件时相同的哈希生成函数"""
        command_str = json.dumps(commands, sort_keys=True)
        return hashlib.sha1(command_str.encode()).hexdigest()

    def decrypt_font(self, obfuscated_font_path, mapping_file_path):
        # 加载混淆字体
        font_res = requests.get(url=obfuscated_font_path, headers=self.header)
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
            glyph_hash = self.hash_glyph_commands(commands)

            # 查找映射表
            if glyph_hash in original_glyph_to_uni:
                unicode_s = original_glyph_to_uni[glyph_hash]
                obfuscated_to_original[unicode_t] = unicode_s

        return obfuscated_to_original

    def get_encrypt_string(self, s, ttf_path):
        # 生成解密映射表
        decryption_map = self.decrypt_font(ttf_path, "mapping_file.json")
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
        modified_s = json.dumps(format_string(modified_data), ensure_ascii=False)
        return modified_s


def clean_string(text):
    """处理字符串:去除HTML标签和换行符"""
    if not isinstance(text, str):
        return text

    # 使用BeautifulSoup去除HTML标签
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text(separator=" ", strip=True)

    # 去除换行符和连续空格
    cleaned = cleaned.replace("\n", " ").replace("\r", "")
    return " ".join(cleaned.split())  # 合并多个空格


def format_string(obj):
    """递归清理JSON数据结构"""
    if isinstance(obj, dict):
        return {k: format_string(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [format_string(elem) for elem in obj]
    elif isinstance(obj, str):
        return clean_string(obj)
    else:
        return obj
