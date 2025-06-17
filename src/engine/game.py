#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
import time
from src.engine.constants import GameState
from src.engine.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.ui.menu import MainMenu
from src.ui.fight_screen import FightScreen
from src.ui.character_select import CharacterSelect

class Game:
    """游戏主类，负责管理游戏状态和主循环"""
    
    def __init__(self):
        """初始化游戏"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MAIN_MENU
        
        # 游戏设置 - 必须在创建UI组件前设置
        self.vsai_mode = False
        self.ai_vs_ai_mode = False  # 新增AI对战AI模式标志
        self.ai_difficulty = 1  # 1-3
        self.selected_characters = [None, None]  # 玩家1和玩家2/AI选择的角色
        
        # 加载游戏组件
        self.main_menu = MainMenu(self)
        self.character_select = CharacterSelect(self)
        self.fight_screen = None
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            # 处理输入
            self._handle_events()
            
            # 更新游戏状态
            self._update()
            
            # 渲染
            self._render()
            
            # 控制帧率
            self.clock.tick(FPS)
    
    def _handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # 根据当前游戏状态处理事件
            if self.state == GameState.MAIN_MENU:
                self.main_menu.handle_event(event)
            elif self.state == GameState.CHARACTER_SELECT:
                self.character_select.handle_event(event)
            elif self.state == GameState.FIGHTING and self.fight_screen:
                self.fight_screen.handle_event(event)
    
    def _update(self):
        """更新游戏状态"""
        if self.state == GameState.MAIN_MENU:
            self.main_menu.update()
        elif self.state == GameState.CHARACTER_SELECT:
            self.character_select.update()
        elif self.state == GameState.FIGHTING and self.fight_screen:
            self.fight_screen.update()
    
    def _render(self):
        """渲染游戏画面"""
        # 清屏
        self.screen.fill((0, 0, 0))
        
        # 根据当前状态渲染相应画面
        if self.state == GameState.MAIN_MENU:
            self.main_menu.render(self.screen)
        elif self.state == GameState.CHARACTER_SELECT:
            self.character_select.render(self.screen)
        elif self.state == GameState.FIGHTING and self.fight_screen:
            self.fight_screen.render(self.screen)
        
        # 更新显示
        pygame.display.flip()
    
    def change_state(self, new_state):
        """改变游戏状态"""
        self.state = new_state
        
        # 状态切换逻辑
        if new_state == GameState.FIGHTING:
            # 创建战斗场景
            self.fight_screen = FightScreen(
                self,
                self.selected_characters[0],
                self.selected_characters[1],
                self.vsai_mode,
                self.ai_difficulty
            )
    
    def start_vs_ai(self, difficulty=1):
        """开始AI对战模式"""
        self.vsai_mode = True
        self.ai_vs_ai_mode = False
        self.ai_difficulty = difficulty
        self.change_state(GameState.CHARACTER_SELECT)
    
    def start_ai_vs_ai(self, difficulty=2):
        """开始AI对战AI模式"""
        self.vsai_mode = True
        self.ai_vs_ai_mode = True
        self.ai_difficulty = difficulty
        self.change_state(GameState.CHARACTER_SELECT)
    
    def start_vs_player(self):
        """开始双人对战模式"""
        self.vsai_mode = False
        self.ai_vs_ai_mode = False
        self.change_state(GameState.CHARACTER_SELECT)
    
    def exit_game(self):
        """退出游戏"""
        self.running = False 