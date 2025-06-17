#!/bin/bash

# 激活Conda环境
source ~/anaconda3/bin/activate fighting-game

# 打印环境信息
echo "使用Python环境: $(which python)"
echo "Python版本: $(python --version)"
echo "Pygame版本: $(python -c 'import pygame; print(f"Pygame {pygame.version.ver}")')"

# 启动游戏
python main.py 