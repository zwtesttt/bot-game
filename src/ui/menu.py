#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import os
from src.engine.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, BLUE, RED, GREEN, YELLOW
from src.engine.constants import GameState
from src.engine.font_utils import get_chinese_font, render_text

class Button:
    """按钮类"""
    
    def __init__(self, x, y, width, height, text, text_color=WHITE, bg_color=BLUE, hover_color=RED):
        """初始化按钮
        
        Args:
            x: 按钮x坐标
            y: 按钮y坐标
            width: 按钮宽度
            height: 按钮高度
            text: 按钮文本
            text_color: 文本颜色
            bg_color: 背景颜色
            hover_color: 悬停颜色
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font_size = 32
    
    def draw(self, screen):
        """绘制按钮
        
        Args:
            screen: 屏幕对象
        """
        # 绘制按钮背景
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)  # 边框
        
        # 绘制按钮文本
        text_surf = render_text(self.text, self.font_size, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def update(self, mouse_pos):
        """更新按钮状态
        
        Args:
            mouse_pos: 鼠标位置
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, event):
        """检查按钮是否被点击
        
        Args:
            event: pygame事件
            
        Returns:
            是否被点击
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False


class MainMenu:
    """主菜单类"""
    
    def __init__(self, game):
        """初始化主菜单
        
        Args:
            game: 游戏实例
        """
        self.game = game
        
        # 菜单项
        button_width = 200
        button_height = 50
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        # 检查机器学习模型是否存在
        self.ml_model_exists = os.path.exists("models/fighting_ai_model.h5")
        
        # 添加AI对战AI选项
        self.buttons = [
            Button(center_x, 200, button_width, button_height, "对战玩家", WHITE, BLUE),
            Button(center_x, 280, button_width, button_height, "对战机器学习AI", WHITE, (128, 0, 128)),  # 紫色
            Button(center_x, 360, button_width, button_height, "AI对战AI", WHITE, (0, 128, 0)),  # 绿色
            Button(center_x, 440, button_width, button_height, "退出游戏", WHITE, (100, 100, 100))
        ]
        
        # 标题
        self.title_text = render_text("格斗之王", 72, WHITE)
        self.title_rect = self.title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    
    def handle_event(self, event):
        """处理菜单事件
        
        Args:
            event: pygame事件
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.buttons):
                if button.is_clicked(event):
                    self._handle_button_click(i)
    
    def _handle_button_click(self, button_index):
        """处理按钮点击
        
        Args:
            button_index: 按钮索引
        """
        if button_index == 0:  # 对战玩家
            self.game.start_vs_player()
        elif button_index == 1:  # 对战机器学习AI
            self.game.start_vs_ai(3)  # 使用困难模式（会启动ML AI）
        elif button_index == 2:  # AI对战AI
            self.game.start_ai_vs_ai(2)  # 使用AI对战AI模式
        elif button_index == 3:  # 退出游戏
            self.game.exit_game()
    
    def update(self):
        """更新菜单状态"""
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
    
    def render(self, screen):
        """渲染菜单
        
        Args:
            screen: 屏幕对象
        """
        # 绘制背景
        screen.fill(BLACK)
        
        # 绘制标题
        screen.blit(self.title_text, self.title_rect)
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(screen) 