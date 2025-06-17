#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
格斗游戏主入口
"""

import pygame
import sys
import os
from src.engine.game import Game
from src.engine.font_utils import get_chinese_font, download_default_font

def main():
    """主函数"""
    # 初始化pygame
    pygame.init()
    pygame.display.set_caption("格斗游戏")
    
    # 显示pygame版本
    print(f"pygame {pygame.version.ver}")
    
    # 初始化中文字体
    print("初始化中文字体...")
    font_path = os.path.join("assets", "fonts", "simhei.ttf")
    if not os.path.exists(font_path):
        print("尝试下载中文字体...")
        try:
            download_default_font()
        except Exception as e:
            print(f"下载字体失败: {e}")
    
    # 测试字体加载
    test_font = get_chinese_font(32)
    print(f"字体初始化完成: {test_font}")
    
    # 创建游戏实例
    game = Game()
    
    # 运行游戏（从主菜单开始）
    game.run()
    
    # 退出pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 