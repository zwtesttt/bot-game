#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
游戏配置文件
"""

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 角色设置
CHARACTER_WIDTH = 100
CHARACTER_HEIGHT = 200
GRAVITY = 0.8
JUMP_FORCE = -15
WALK_SPEED = 5
RUN_SPEED = 8

# 攻击设置
LIGHT_PUNCH_DAMAGE = 5
HEAVY_PUNCH_DAMAGE = 10
LIGHT_KICK_DAMAGE = 7
HEAVY_KICK_DAMAGE = 12

# 血量设置
MAX_HEALTH = 100

# 游戏时间
ROUND_TIME = 99  # 秒

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 资源路径
ASSETS_DIR = "assets"
IMAGES_DIR = f"{ASSETS_DIR}/images"
SOUNDS_DIR = f"{ASSETS_DIR}/sounds"

# AI设置
AI_REACTION_TIME = {
    1: 0.3,  # 简单难度：0.3秒反应时间（原为0.5秒）
    2: 0.15,  # 中等难度：0.15秒反应时间（原为0.3秒）
    3: 0.05   # 困难难度：0.05秒反应时间（原为0.1秒）
}
AI_DECISION_INTERVAL = {
    1: 0.5,  # 简单难度：每0.5秒决策一次（原为1.0秒）
    2: 0.3,  # 中等难度：每0.3秒决策一次（原为0.5秒）
    3: 0.1   # 困难难度：每0.1秒决策一次（原为0.2秒）
} 