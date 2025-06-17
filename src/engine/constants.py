#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
游戏常量和枚举
"""

from enum import Enum

class GameState(Enum):
    """游戏状态枚举"""
    MAIN_MENU = 0
    CHARACTER_SELECT = 1
    FIGHTING = 2
    GAME_OVER = 3 