import json
from fontTools.ttLib import TTFont
import hashlib

def is_chinese_char(unicodes):
    """检查Unicode码点是否属于中文字符范围"""
    return any(0x4E00 <= u <= 0x9FFF for u in unicodes)

def hash_glyph_commands(commands):
    """将路径命令转换为哈希（示例实现需根据实际数据结构调整）"""
    # 这里假设commands是类似opentype.js的路径命令对象
    # 需要将其转换为可哈希的字符串表示
    command_str = json.dumps(commands, sort_keys=True)
    return hashlib.sha1(command_str.encode()).hexdigest()

# 加载字体文件
font = TTFont('SourceHanSansSC-VF.ttf')
cmap = font.getBestCmap()

# 构建字形名称到Unicode的反向映射
glyph_unicodes = {}
for code, name in cmap.items():
    glyph_unicodes.setdefault(name, []).append(code)

glyphs_to_uni = {}

# 遍历所有字形
for glyph_name in font.getGlyphOrder():
    # 获取对应的Unicode码点
    unicodes = glyph_unicodes.get(glyph_name, [])
    
    if is_chinese_char(unicodes):
        glyph = font['glyf'][glyph_name]
        
        commands = []
        if glyph.numberOfContours > 0:
            # 简单字形
            end_pts = glyph.endPtsOfContours
            flags = glyph.flags
            coords = glyph.coordinates
            # 转换为命令表示（示例简化）
            commands = [f"CONTOUR_END:{end_pts}", f"COORDS:{coords}"]
        elif glyph.isComposite():
            # 复合字形
            components = [f"{comp.glyphName}({comp.x},{comp.y})" 
                         for comp in glyph.components]
            commands = ["COMPOSITE"] + components
        
        # 生成哈希
        glyph_hash = hash_glyph_commands(commands)
        
        # 存储第一个Unicode码点
        if glyph_hash not in glyphs_to_uni:
            glyphs_to_uni[glyph_hash] = unicodes[0]

# 保存结果
with open('mapping_file.json', 'w', encoding='utf-8') as f:
    json.dump(glyphs_to_uni, f, ensure_ascii=False, indent=2)