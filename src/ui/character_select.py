#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import random
import os
from src.engine.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, BLUE, RED, GREEN, YELLOW
from src.engine.constants import GameState
from src.characters.ryu import Ryu
from src.characters.ken import Ken
from src.characters.chun_li import ChunLi
from src.ui.menu import Button
from src.engine.font_utils import get_chinese_font, render_text

class CharacterCard:
    """角色卡片类"""
    
    def __init__(self, x, y, width, height, character_name, preview_color=BLUE):
        """初始化角色卡片
        
        Args:
            x: 卡片x坐标
            y: 卡片y坐标
            width: 卡片宽度
            height: 卡片高度
            character_name: 角色名称
            preview_color: 预览颜色
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.character_name = character_name
        self.preview_color = preview_color
        self.is_selected = False
        self.is_hovered = False
        self.font_size = 24
        
        # 加载角色预览图
        self.preview_image = None
        preview_path = os.path.join("assets", "images", "characters", character_name.lower().replace(" ", "-"), "idle.png")
        if os.path.exists(preview_path):
            try:
                sprite_sheet = pygame.image.load(preview_path).convert_alpha()
                # 从精灵表中提取第一帧作为预览
                sprite_width = sprite_sheet.get_width() // 4  # idle精灵表有4帧
                sprite_height = sprite_sheet.get_height()
                
                # 创建一个新的Surface并将精灵的一部分绘制到其上
                self.preview_image = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                self.preview_image.blit(sprite_sheet, (0, 0), (0, 0, sprite_width, sprite_height))
                
                # 调整大小以适应卡片
                preview_width = width - 20
                preview_height = height - 40
                scale_factor = min(preview_width / sprite_width, preview_height / sprite_height)
                new_width = int(sprite_width * scale_factor)
                new_height = int(sprite_height * scale_factor)
                self.preview_image = pygame.transform.scale(self.preview_image, (new_width, new_height))
            except Exception as e:
                print(f"加载角色预览图失败: {e}")
                self.preview_image = None
    
    def draw(self, screen):
        """绘制角色卡片
        
        Args:
            screen: 屏幕对象
        """
        # 卡片背景
        bg_color = GREEN if self.is_selected else (RED if self.is_hovered else self.preview_color)
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)  # 边框
        
        # 角色预览
        preview_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 10,
            self.rect.width - 20,
            self.rect.height - 40
        )
        
        if self.preview_image:
            # 计算居中位置
            x_offset = self.rect.x + (self.rect.width - self.preview_image.get_width()) // 2
            y_offset = self.rect.y + 10
            screen.blit(self.preview_image, (x_offset, y_offset))
        else:
            # 如果没有预览图，使用纯色块
            pygame.draw.rect(screen, self.preview_color, preview_rect)
        
        # 角色名称
        text_surf = render_text(self.character_name, self.font_size, WHITE)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 20))
        screen.blit(text_surf, text_rect)
    
    def update(self, mouse_pos):
        """更新卡片状态
        
        Args:
            mouse_pos: 鼠标位置
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, event):
        """检查卡片是否被点击
        
        Args:
            event: pygame事件
            
        Returns:
            是否被点击
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False


class CharacterSelect:
    """角色选择界面"""
    
    def __init__(self, game):
        """初始化角色选择界面
        
        Args:
            game: 游戏实例
        """
        self.game = game
        
        # 标题
        self.title_text = render_text("选择角色", 48, WHITE)
        self.title_rect = self.title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        
        # 角色卡片
        card_width = 150
        card_height = 200
        padding = 30
        total_width = (card_width + padding) * 3 - padding
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        self.character_cards = [
            CharacterCard(start_x, 100, card_width, card_height, "Ryu", BLUE),
            CharacterCard(start_x + card_width + padding, 100, card_width, card_height, "Ken", RED),
            CharacterCard(start_x + (card_width + padding) * 2, 100, card_width, card_height, "Chun-Li", GREEN)
        ]
        
        # 玩家选择提示
        if game.ai_vs_ai_mode:
            self.player_text = "选择AI 1角色"
        elif game.vsai_mode:
            self.player_text = "选择你的角色"
        else:
            self.player_text = "玩家1选择"
        
        self.player_text_surf = render_text(self.player_text, 36, WHITE)
        self.player_text_rect = self.player_text_surf.get_rect(center=(SCREEN_WIDTH // 2, 350))
        
        # 确认和返回按钮
        self.confirm_button = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 50, "确认", WHITE, GREEN)
        self.back_button = Button(SCREEN_WIDTH // 2 - 100, 470, 200, 50, "返回", WHITE, RED)
        
        # 选择状态
        self.selection_state = 0  # 0: 玩家1选择, 1: 玩家2选择, 2: 已完成
        self.player1_selection = None
        self.player2_selection = None
        
        # 添加键位功能描述
        self.show_controls = True
        self.controls_panel = self._create_controls_panel()
    
    def _create_controls_panel(self):
        """创建控制键位面板
        
        Returns:
            控制面板Surface
        """
        panel_width, panel_height = 700, 160
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 180), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel, WHITE, (0, 0, panel_width, panel_height), 2)
        
        # 标题
        title = render_text("游戏控制", 24, YELLOW)
        panel.blit(title, (panel_width // 2 - title.get_width() // 2, 10))
        
        # 绘制玩家1控制键
        p1_title = render_text("玩家1控制:", 20, BLUE)
        panel.blit(p1_title, (20, 40))
        
        p1_controls = [
            "W - 跳跃",
            "A - 左移",
            "S - 蹲下",
            "D - 右移",
            "J - 轻拳",
            "K - 重拳",
            "L - 轻腿",
            "; - 重腿",
            "空格 - 格挡"
        ]
        
        # 绘制玩家2控制键
        p2_title = render_text("玩家2控制:", 20, RED)
        panel.blit(p2_title, (panel_width // 2 + 20, 40))
        
        p2_controls = [
            "↑ - 跳跃",
            "← - 左移",
            "↓ - 蹲下",
            "→ - 右移",
            "小键盘1 - 轻拳",
            "小键盘2 - 重拳",
            "小键盘3 - 轻腿",
            "小键盘4 - 重腿",
            "小键盘0 - 格挡"
        ]
        
        # 绘制控制说明
        font_size = 16
        y_offset = 65
        for i, text in enumerate(p1_controls):
            if i < 5:  # 前5个放在第一列
                control_text = render_text(text, font_size, WHITE)
                panel.blit(control_text, (30, y_offset + i * 18))
            else:  # 后面的放在第二列
                control_text = render_text(text, font_size, WHITE)
                panel.blit(control_text, (150, y_offset + (i - 5) * 18))
        
        for i, text in enumerate(p2_controls):
            if i < 5:  # 前5个放在第一列
                control_text = render_text(text, font_size, WHITE)
                panel.blit(control_text, (panel_width // 2 + 30, y_offset + i * 18))
            else:  # 后面的放在第二列
                control_text = render_text(text, font_size, WHITE)
                panel.blit(control_text, (panel_width // 2 + 150, y_offset + (i - 5) * 18))
        
        return panel
    
    def handle_event(self, event):
        """处理事件
        
        Args:
            event: pygame事件
        """
        # 处理角色卡片点击
        for i, card in enumerate(self.character_cards):
            if card.is_clicked(event):
                self._handle_card_selection(i)
        
        # 处理按钮点击
        if self.confirm_button.is_clicked(event):
            self._handle_confirm()
        
        if self.back_button.is_clicked(event):
            self._handle_back()
        
        # 键盘控制: H键切换控制说明显示
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            self.show_controls = not self.show_controls
    
    def _handle_card_selection(self, card_index):
        """处理角色卡片选择
        
        Args:
            card_index: 卡片索引
        """
        # 清除之前的选择
        for card in self.character_cards:
            card.is_selected = False
        
        # 设置新选择
        self.character_cards[card_index].is_selected = True
        
        # 更新选择状态
        if self.selection_state == 0:  # 玩家1/AI1选择
            self.player1_selection = card_index
            
            # 如果是AI对战AI模式，切换到AI2选择
            if self.game.ai_vs_ai_mode:
                self.selection_state = 1
                self.player_text = "选择AI 2角色"
                self.player_text_surf = render_text(self.player_text, 36, WHITE)
            # 如果是AI模式，直接完成选择
            elif self.game.vsai_mode:
                self.selection_state = 2
                # 对AI随机选择一个不同的角色
                available_indices = [i for i in range(len(self.character_cards)) if i != card_index]
                self.player2_selection = random.choice(available_indices)
            else:
                # 切换到玩家2选择
                self.selection_state = 1
                self.player_text = "玩家2选择"
                self.player_text_surf = render_text(self.player_text, 36, WHITE)
        
        elif self.selection_state == 1:  # 玩家2/AI2选择
            self.player2_selection = card_index
            self.selection_state = 2
    
    def _handle_confirm(self):
        """处理确认按钮点击"""
        # 只有在有选择的情况下才能确认
        if self.selection_state == 2:
            # 创建选择的角色
            player1_char = self._create_character(self.player1_selection, 100, 400)
            player2_char = self._create_character(self.player2_selection, 600, 400)
            
            # 设置游戏角色
            self.game.selected_characters[0] = player1_char
            self.game.selected_characters[1] = player2_char
            
            # 切换到战斗状态
            self.game.change_state(GameState.FIGHTING)
    
    def _handle_back(self):
        """处理返回按钮点击"""
        self.game.change_state(GameState.MAIN_MENU)
    
    def _create_character(self, selection_index, x, y):
        """根据选择创建角色
        
        Args:
            selection_index: 选择索引
            x: 初始x坐标
            y: 初始y坐标
            
        Returns:
            创建的角色实例
        """
        char_name = self.character_cards[selection_index].character_name
        
        # 根据角色名称创建不同的角色实例
        if char_name == "Ryu":
            return Ryu(x, y)
        elif char_name == "Ken":
            return Ken(x, y)
        elif char_name == "Chun-Li":
            return ChunLi(x, y)
        
        # 默认返回Ryu
        return Ryu(x, y)
    
    def update(self):
        """更新界面状态"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新角色卡片
        for card in self.character_cards:
            card.update(mouse_pos)
        
        # 更新按钮
        self.confirm_button.update(mouse_pos)
        self.back_button.update(mouse_pos)
        
        # 确认按钮只有在选择完成时才可用
        self.confirm_button.bg_color = GREEN if self.selection_state == 2 else (100, 100, 100)
    
    def render(self, screen):
        """渲染界面
        
        Args:
            screen: 屏幕对象
        """
        # 绘制背景
        screen.fill(BLACK)
        
        # 绘制标题
        screen.blit(self.title_text, self.title_rect)
        
        # 绘制角色卡片
        for card in self.character_cards:
            card.draw(screen)
        
        # 绘制玩家选择提示
        screen.blit(self.player_text_surf, self.player_text_rect)
        
        # 绘制按钮
        self.confirm_button.draw(screen)
        self.back_button.draw(screen)
        
        # 绘制选择提示
        if self.player1_selection is not None and not self.game.vsai_mode:
            text = "玩家1: " + self.character_cards[self.player1_selection].character_name
            text_surf = render_text(text, 36, BLUE)
            screen.blit(text_surf, (50, 350))
        
        if self.player2_selection is not None and not self.game.vsai_mode:
            text = "玩家2: " + self.character_cards[self.player2_selection].character_name
            text_surf = render_text(text, 36, RED)
            screen.blit(text_surf, (SCREEN_WIDTH - 250, 350))
        
        # 绘制控制说明面板
        if self.show_controls:
            panel_x = (SCREEN_WIDTH - self.controls_panel.get_width()) // 2
            panel_y = SCREEN_HEIGHT - self.controls_panel.get_height() - 20
            screen.blit(self.controls_panel, (panel_x, panel_y))
            
            # 绘制切换提示
            toggle_text = render_text("按 H 键隐藏/显示控制说明", 16, YELLOW)
            toggle_rect = toggle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 10))
            screen.blit(toggle_text, toggle_rect)
        else:
            # 如果控制面板隐藏，只显示简短提示
            hint_text = render_text("按 H 键显示控制说明", 16, YELLOW)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
            screen.blit(hint_text, hint_rect) 