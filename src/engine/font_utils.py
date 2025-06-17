#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
字体工具模块，处理中文字体加载
"""

import os
import pygame
import sys
import platform

# 确保assets/fonts目录存在
fonts_dir = os.path.join("assets", "fonts")
os.makedirs(fonts_dir, exist_ok=True)

# 默认字体路径
DEFAULT_FONT_PATH = os.path.join(fonts_dir, "simhei.ttf")

# 备用内置字体路径
BUILTIN_FONTS = []

# 检测操作系统并添加系统字体路径
system = platform.system()
if system == 'Darwin':  # macOS
    # 添加macOS常用中文字体路径
    BUILTIN_FONTS.extend([
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/Library/Fonts/Arial Unicode.ttf',
        os.path.expanduser('~/Library/Fonts/Microsoft YaHei.ttf')
    ])
elif system == 'Windows':
    # 添加Windows常用中文字体路径
    BUILTIN_FONTS.extend([
        'C:\\Windows\\Fonts\\simhei.ttf',
        'C:\\Windows\\Fonts\\msyh.ttf',
        'C:\\Windows\\Fonts\\simsun.ttc'
    ])
elif system == 'Linux':
    # 添加Linux常用中文字体路径
    BUILTIN_FONTS.extend([
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc'
    ])

# 是否找到了支持中文的字体
has_chinese_font = False
font_cache = {}  # 字体缓存

# 尝试加载系统中支持中文的字体
def get_chinese_font(size=32):
    """获取支持中文的字体
    
    Args:
        size: 字体大小
        
    Returns:
        pygame.font.Font对象
    """
    global has_chinese_font, font_cache
    
    # 检查缓存
    cache_key = f"size_{size}"
    if cache_key in font_cache:
        return font_cache[cache_key]
    
    # 首先尝试使用自带的默认字体
    if os.path.exists(DEFAULT_FONT_PATH):
        try:
            font = pygame.font.Font(DEFAULT_FONT_PATH, size)
            has_chinese_font = True
            font_cache[cache_key] = font
            return font
        except Exception as e:
            print(f"加载默认字体失败: {e}")
    
    # 尝试使用内置系统字体
    for font_path in BUILTIN_FONTS:
        if os.path.exists(font_path):
            try:
                font = pygame.font.Font(font_path, size)
                has_chinese_font = True
                font_cache[cache_key] = font
                print(f"成功加载系统字体: {font_path}")
                return font
            except Exception as e:
                print(f"加载系统字体 {font_path} 失败: {e}")
    
    # 如果内置字体不存在，尝试系统字体名称
    # 常见支持中文的字体列表
    chinese_fonts = [
        'SimHei',           # 黑体
        'Microsoft YaHei',  # 微软雅黑
        'SimSun',           # 宋体
        'NSimSun',          # 新宋体
        'FangSong',         # 仿宋
        'KaiTi',            # 楷体
        'Arial Unicode MS', # Arial Unicode
        'Heiti SC',         # 黑体-简 (macOS)
        'PingFang SC',      # 苹方-简 (macOS)
        'STHeiti',          # 华文黑体 (macOS)
        'Noto Sans CJK SC', # Noto Sans CJK SC (Linux)
        'WenQuanYi Micro Hei', # 文泉驿微米黑 (Linux)
        'Hiragino Sans GB',    # macOS 中文字体
    ]
    
    # 尝试每一个中文字体
    for font_name in chinese_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试字体是否能渲染中文
            test_surf = font.render("测试", True, (255, 255, 255))
            has_chinese_font = True
            font_cache[cache_key] = font
            print(f"成功加载字体: {font_name}")
            return font
        except Exception as e:
            continue
    
    # 如果所有系统字体都失败，返回备选方案
    print("警告: 未找到支持中文的字体，使用备选方案")
    has_chinese_font = False
    
    # 使用pygame默认字体，但不渲染中文字符
    default_font = pygame.font.SysFont(None, size)
    font_cache[cache_key] = default_font
    return default_font

def render_text(text, size=32, color=(255, 255, 255)):
    """渲染文本
    
    Args:
        text: 要渲染的文本
        size: 字体大小
        color: 文本颜色
        
    Returns:
        渲染好的文本Surface
    """
    font = get_chinese_font(size)
    
    # 如果没有中文字体支持，替换中文为英文提示
    if not has_chinese_font:
        # 检测文本是否包含中文
        has_chinese = any(u'\u4e00' <= char <= u'\u9fff' for char in text)
        if has_chinese:
            # 提取英文和数字
            eng_text = ''.join(char if char.isascii() else '' for char in text)
            # 如果没有英文，使用替代文本
            if not eng_text:
                if "玩家" in text:
                    eng_text = "Player"
                elif "对战" in text:
                    eng_text = "VS"
                elif "简单" in text:
                    eng_text = "Easy"
                elif "中等" in text:
                    eng_text = "Medium"
                elif "困难" in text:
                    eng_text = "Hard"
                elif "退出" in text:
                    eng_text = "Exit"
                elif "确认" in text:
                    eng_text = "Confirm"
                elif "返回" in text:
                    eng_text = "Back"
                elif "选择" in text:
                    eng_text = "Select"
                elif "胜利" in text:
                    eng_text = "Win"
                elif "平局" in text:
                    eng_text = "Draw"
                elif "主菜单" in text:
                    eng_text = "Main Menu"
                elif "格斗之王" in text:
                    eng_text = "Fighting King"
                elif "训练" in text:
                    eng_text = "Training"
                elif "冷却" in text:
                    eng_text = "Cooldown"
                elif "秒" in text:
                    eng_text = "sec"
                elif "攻击" in text:
                    eng_text = "Attack"
                else:
                    eng_text = "Text"
            text = eng_text
    
    return font.render(text, True, color)

def download_default_font():
    """尝试下载默认中文字体"""
    if os.path.exists(DEFAULT_FONT_PATH):
        return True
    
    try:
        import requests
        print("尝试下载默认中文字体...")
        
        # 这是一个更可靠的开源中文字体的URL (思源黑体)
        font_url = "https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSansSC.zip"
        
        # 临时文件路径
        zip_path = os.path.join(fonts_dir, "temp_font.zip")
        
        # 下载字体
        response = requests.get(font_url, stream=True)
        response.raise_for_status()
        
        # 保存zip文件
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # 解压文件
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 只提取我们需要的Regular字体文件
            for file in zip_ref.namelist():
                if "SourceHanSansSC-Regular" in file and file.endswith(".otf"):
                    zip_ref.extract(file, fonts_dir)
                    # 重命名为我们期望的文件名
                    os.rename(os.path.join(fonts_dir, file), DEFAULT_FONT_PATH)
                    break
        
        # 清理临时文件
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        print(f"字体下载成功，保存到 {DEFAULT_FONT_PATH}")
        return True
    except Exception as e:
        print(f"下载字体失败: {e}")
        return False

# 游戏启动时尝试下载字体
try:
    # 立即尝试下载字体，不使用后台线程，确保字体在游戏开始前可用
    if not os.path.exists(DEFAULT_FONT_PATH):
        download_default_font()
except Exception as e:
    print(f"初始化字体失败: {e}")
    pass 