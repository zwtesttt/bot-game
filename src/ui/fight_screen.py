#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import time
import os
import math
import random
from src.engine.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, BLUE, RED, GREEN, YELLOW, ROUND_TIME
from src.engine.constants import GameState
from src.ai.ai_controller import AIController
from src.ai.custom_ai import MLBasedAI
from src.engine.font_utils import get_chinese_font, render_text

class FightScreen:
    """战斗界面"""
    
    def __init__(self, game, player1, player2, vsai_mode=False, ai_difficulty=1):
        """初始化战斗界面
        
        Args:
            game: 游戏实例
            player1: 玩家1角色
            player2: 玩家2/AI角色
            vsai_mode: 是否为AI对战模式
            ai_difficulty: AI难度 (1-3)
        """
        self.game = game
        self.player1 = player1
        self.player2 = player2
        self.vsai_mode = vsai_mode
        self.ai_vs_ai_mode = game.ai_vs_ai_mode
        
        # 设置角色名称，方便调试
        if self.ai_vs_ai_mode:
            self.player1.name = "AI 1"
            self.player2.name = "AI 2"
        elif vsai_mode:
            self.player1.name = "玩家1"
            self.player2.name = "AI"
        else:
            self.player1.name = "玩家1"
            self.player2.name = "玩家2"
        
        # 创建AI控制器（如果是AI模式）
        self.ai_controller = None
        self.ml_ai_controller = None
        self.ai1_controller = None
        self.ml_ai1_controller = None
        
        if self.ai_vs_ai_mode:
            # AI对战AI模式：为两个角色都创建AI控制器
            if ai_difficulty == 3:
                self.ml_ai1_controller = MLBasedAI(player1)
                self.ml_ai_controller = MLBasedAI(player2)
            else:
                # 为两个AI分配不同的行为模式
                self.ai1_controller = AIController(player1, ai_difficulty, "aggressive")
                self.ai_controller = AIController(player2, ai_difficulty, "defensive")
        elif vsai_mode:
            # 玩家对战AI模式：只为玩家2创建AI控制器
            if ai_difficulty == 3:
                self.ml_ai_controller = MLBasedAI(player2)
            else:
                self.ai_controller = AIController(player2, ai_difficulty, "balanced")
        
        # 设置角色位置 - 修改初始位置，使角色之间的距离更远
        self.player1.x = 30  # 进一步向左移动（原为50）
        self.player1.y = 400 - self.player1.height
        self.player2.x = 670  # 进一步向右移动（原为650）
        self.player2.y = 400 - self.player2.height
        
        # 游戏状态
        self.round_time = ROUND_TIME
        self.round_start_time = time.time()
        self.round_over = False
        self.winner = None
        
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(player1)
        self.all_sprites.add(player2)
        
        # 加载背景图像
        self.background_image = None
        bg_path = os.path.join("assets", "images", "backgrounds", "stage1.jpg")
        if os.path.exists(bg_path):
            try:
                self.background_image = pygame.image.load(bg_path).convert()
                # 调整背景图像大小以适应屏幕
                self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception as e:
                print(f"加载背景图像失败: {e}")
        
        # 背景颜色（作为备用）
        self.background_color = (50, 50, 100)
        
        # 按键状态
        self.key_state = {
            # 玩家1控制
            pygame.K_w: False,  # 跳跃
            pygame.K_a: False,  # 左移
            pygame.K_s: False,  # 蹲下
            pygame.K_d: False,  # 右移
            pygame.K_j: False,  # 轻拳
            pygame.K_k: False,  # 重拳
            pygame.K_l: False,  # 轻腿
            pygame.K_SEMICOLON: False,  # 重腿
            pygame.K_SPACE: False,  # 格挡
            
            # 玩家2控制
            pygame.K_UP: False,    # 跳跃
            pygame.K_LEFT: False,  # 左移
            pygame.K_DOWN: False,  # 蹲下
            pygame.K_RIGHT: False, # 右移
            pygame.K_KP1: False,   # 轻拳
            pygame.K_KP2: False,   # 重拳
            pygame.K_KP3: False,   # 轻腿
            pygame.K_KP4: False,   # 重腿
            pygame.K_KP0: False    # 格挡
        }
        
        # 特效系统
        self.effects = []  # 存储活跃的特效
        self.damage_created_this_frame = set()  # 跟踪在当前帧已创建的伤害效果
        self.last_effect_cleanup = time.time()  # 上次清理特效的时间
        
        # 新增：伤害防抖和跟踪系统
        self.last_damage_time = {
            self.player1.name: 0,
            self.player2.name: 0
        }  # 每个角色上次受伤的时间
        self.damage_debounce_time = 0.5  # 增加防抖时间，单位秒，两次伤害特效的最小时间间隔
        self.active_damage_ids = set()  # 当前活跃的伤害ID
        self.registered_hits = {}  # 记录已经处理的命中 {hit_id: timestamp}
        
        # 预定义特效颜色
        self.effect_colors = {
            "light_punch": (255, 255, 0, 180),  # 黄色，半透明
            "heavy_punch": (255, 165, 0, 200),  # 橙色，更不透明
            "light_kick": (0, 255, 255, 180),   # 青色
            "heavy_kick": (255, 0, 0, 200),     # 红色
            "hit": (255, 255, 255, 220)         # 白色，表示受击
        }
        
        # 上一帧的角色状态，用于检测状态变化
        self.p1_last_state = self.player1.state
        self.p2_last_state = self.player2.state
        self.p1_last_health = self.player1.health
        self.p2_last_health = self.player2.health
    
    def handle_event(self, event):
        """处理事件
        
        Args:
            event: pygame事件
        """
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_state:
                self.key_state[event.key] = True
        
        elif event.type == pygame.KEYUP:
            if event.key in self.key_state:
                self.key_state[event.key] = False
            
            # 特殊操作：退出战斗（按ESC键）
            if event.key == pygame.K_ESCAPE:
                self.game.change_state(GameState.MAIN_MENU)
    
    def update(self):
        """更新战斗状态"""
        dt = 1.0 / 60  # 假设60帧每秒
        
        # 更新回合时间
        current_time = time.time()
        elapsed_time = current_time - self.round_start_time
        self.round_time = max(0, ROUND_TIME - elapsed_time)
        
        # 如果回合结束，不再更新
        if self.round_over:
            return
        
        # 检查回合是否结束
        if self.round_time <= 0 or self.player1.health <= 0 or self.player2.health <= 0:
            self.round_over = True
            
            # 决定胜者
            if self.player1.health <= 0:
                self.winner = self.player2
            elif self.player2.health <= 0:
                self.winner = self.player1
            elif self.player1.health > self.player2.health:
                self.winner = self.player1
            elif self.player2.health > self.player1.health:
                self.winner = self.player2
            else:
                self.winner = None  # 平局
            
            return
        
        # 处理玩家1控制（或AI1）
        if self.ai_vs_ai_mode:
            # AI1控制玩家1
            if self.ml_ai1_controller:
                self.ml_ai1_controller.update(dt, self.player2)
            elif self.ai1_controller:
                self.ai1_controller.update(dt, self.player2)
        else:
            # 玩家控制
            self._handle_player_controls(self.player1, True)
        
        # 处理玩家2控制（或AI）
        if self.vsai_mode:
            # AI控制玩家2
            if self.ml_ai_controller:
                self.ml_ai_controller.update(dt, self.player1)
            elif self.ai_controller:
                self.ai_controller.update(dt, self.player1)
        else:
            # 玩家控制
            self._handle_player_controls(self.player2, False)
        
        # 更新角色
        self.player1.update(dt, self.player2)
        self.player2.update(dt, self.player1)
        
        # 检查和清理特效 - 优化特效限制提高流畅度
        if len(self.effects) > 5:  # 进一步降低特效上限
            self._clean_effects()
            
        # 执行正常的特效检测和创建
        # 检测攻击，创建视觉特效
        self._check_attack_effects(self.player1, self.player2, self.p1_last_state, self.p1_last_health)
        self._check_attack_effects(self.player2, self.player1, self.p2_last_state, self.p2_last_health)
        
        # 更新特效
        self._update_effects(dt)
        
        # 清空当前帧已创建的伤害效果记录（在每帧结束时重置）
        self.damage_created_this_frame.clear()
        
        # 每0.25秒强制清理一次特效，进一步提高流畅性
        if current_time - self.last_effect_cleanup > 0.25:
            self._clean_effects()
            self.last_effect_cleanup = current_time
        
        # 保存当前状态用于下一帧比较
        self.p1_last_state = self.player1.state
        self.p2_last_state = self.player2.state
        self.p1_last_health = self.player1.health
        self.p2_last_health = self.player2.health
    
    def _handle_player_controls(self, player, is_player_one):
        """处理玩家控制
        
        Args:
            player: 玩家角色
            is_player_one: 是否为玩家1
        """
        # 获取相应的按键集
        if is_player_one:
            # 玩家1控制
            if self.key_state[pygame.K_a]:
                player.move_left()
            elif self.key_state[pygame.K_d]:
                player.move_right()
            else:
                player.stop_moving()
            
            if self.key_state[pygame.K_w]:
                player.jump()
            
            if self.key_state[pygame.K_s]:
                player.crouch()
            elif not self.key_state[pygame.K_s] and player.is_crouching:
                player.stand_up()
            
            if self.key_state[pygame.K_SPACE]:
                player.block()
            elif not self.key_state[pygame.K_SPACE] and player.is_blocking:
                player.stop_blocking()
            
            if self.key_state[pygame.K_j]:
                player.light_punch()
            elif self.key_state[pygame.K_k]:
                player.heavy_punch()
            elif self.key_state[pygame.K_l]:
                player.light_kick()
            elif self.key_state[pygame.K_SEMICOLON]:
                player.heavy_kick()
        else:
            # 玩家2控制
            if self.key_state[pygame.K_LEFT]:
                player.move_left()
            elif self.key_state[pygame.K_RIGHT]:
                player.move_right()
            else:
                player.stop_moving()
            
            if self.key_state[pygame.K_UP]:
                player.jump()
            
            if self.key_state[pygame.K_DOWN]:
                player.crouch()
            elif not self.key_state[pygame.K_DOWN] and player.is_crouching:
                player.stand_up()
            
            if self.key_state[pygame.K_KP0]:
                player.block()
            elif not self.key_state[pygame.K_KP0] and player.is_blocking:
                player.stop_blocking()
            
            if self.key_state[pygame.K_KP1]:
                player.light_punch()
            elif self.key_state[pygame.K_KP2]:
                player.heavy_punch()
            elif self.key_state[pygame.K_KP3]:
                player.light_kick()
            elif self.key_state[pygame.K_KP4]:
                player.heavy_kick()
    
    def render(self, screen):
        """渲染战斗界面
        
        Args:
            screen: 屏幕对象
        """
        # 绘制背景
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(self.background_color)
        
        # 绘制战斗平台
        platform_rect = pygame.Rect(0, 400, SCREEN_WIDTH, SCREEN_HEIGHT - 400)
        platform_color = (100, 70, 40, 180)  # 半透明平台
        platform_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - 400), pygame.SRCALPHA)
        pygame.draw.rect(platform_surface, platform_color, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 400))
        screen.blit(platform_surface, (0, 400))
        
        # 绘制所有精灵
        self.all_sprites.draw(screen)
        
        # 绘制特效
        self._render_effects(screen)
        
        # 绘制UI元素
        self._draw_ui(screen)
        
        # 如果回合结束，显示结果
        if self.round_over:
            self._draw_round_result(screen)
    
    def _draw_ui(self, screen):
        """绘制UI元素
        
        Args:
            screen: 屏幕对象
        """
        # 绘制血条
        self._draw_health_bar(screen, 50, 50, self.player1.health, 100, BLUE)
        self._draw_health_bar(screen, SCREEN_WIDTH - 350, 50, self.player2.health, 100, RED)
        
        # 绘制攻击冷却指示器
        if self.player1.attack_cooldown > 0:
            self._draw_cooldown_indicator(screen, 50, 75, self.player1.attack_cooldown, self.player1.attack_cooldown_duration, BLUE)
            
        if self.player2.attack_cooldown > 0:
            self._draw_cooldown_indicator(screen, SCREEN_WIDTH - 350, 75, self.player2.attack_cooldown, self.player2.attack_cooldown_duration, RED)
        
        # 绘制玩家名称和血条上方的标签
        if self.ai_vs_ai_mode:
            # 使用大字体绘制名称，并放在血条正上方
            p1_name_text = "AI 1"
            p2_name_text = "AI 2"
            
            # 确保名称字符串已设置
            if hasattr(self.player1, 'name') and self.player1.name:
                p1_name_text = self.player1.name
            if hasattr(self.player2, 'name') and self.player2.name:
                p2_name_text = self.player2.name
                
            # 渲染名称文本
            p1_name = render_text(p1_name_text, 30, BLUE)
            p2_name = render_text(p2_name_text, 30, RED)
            
            # 计算文本位置，使其位于血条上方中央
            p1_name_rect = p1_name.get_rect(centerx=50+150, bottom=40)  # 血条中心位置
            p2_name_rect = p2_name.get_rect(centerx=SCREEN_WIDTH-350+150, bottom=40)
            
            # 绘制名称
            screen.blit(p1_name, p1_name_rect)
            screen.blit(p2_name, p2_name_rect)
            
            # 在AI名称下方显示行为模式
            if self.ai1_controller:
                behavior1_text = render_text("(进攻型)", 16, BLUE)
                behavior1_rect = behavior1_text.get_rect(centerx=p1_name_rect.centerx, top=p1_name_rect.bottom + 2)
                screen.blit(behavior1_text, behavior1_rect)
            if self.ai_controller:
                behavior2_text = render_text("(防守型)", 16, RED)
                behavior2_rect = behavior2_text.get_rect(centerx=p2_name_rect.centerx, top=p2_name_rect.bottom + 2)
                screen.blit(behavior2_text, behavior2_rect)
                
            # 在顶部添加模式标题
            mode_text = render_text("AI对战AI模式", 24, YELLOW)
            mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
            screen.blit(mode_text, mode_rect)
        else:
            # 非AI对战模式的名称显示
            p1_name_text = "玩家1"
            p2_name_text = "玩家2" if not self.vsai_mode else "AI"
            
            # 确保名称字符串已设置
            if hasattr(self.player1, 'name') and self.player1.name:
                p1_name_text = self.player1.name
            if hasattr(self.player2, 'name') and self.player2.name:
                p2_name_text = self.player2.name
                
            # 渲染名称文本
            p1_name = render_text(p1_name_text, 30, BLUE)
            p2_name = render_text(p2_name_text, 30, RED)
            
            # 计算文本位置，使其位于血条上方中央
            p1_name_rect = p1_name.get_rect(centerx=50+150, bottom=40)
            p2_name_rect = p2_name.get_rect(centerx=SCREEN_WIDTH-350+150, bottom=40)
            
            # 绘制名称
            screen.blit(p1_name, p1_name_rect)
            screen.blit(p2_name, p2_name_rect)
        
        # 绘制回合时间
        time_text = render_text(f"{int(self.round_time)}", 48, YELLOW)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(time_text, time_rect)
    
    def _draw_health_bar(self, screen, x, y, health, max_health, color):
        """绘制血条
        
        Args:
            screen: 屏幕对象
            x: 血条x坐标
            y: 血条y坐标
            health: 当前生命值
            max_health: 最大生命值
            color: 血条颜色
        """
        # 计算血条宽度
        bar_width = 300
        fill_width = int((health / max_health) * bar_width)
        
        # 绘制边框
        border_rect = pygame.Rect(x, y, bar_width, 20)
        pygame.draw.rect(screen, WHITE, border_rect, 2)
        
        # 绘制血条
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, 20)
            pygame.draw.rect(screen, color, fill_rect)
    
    def _draw_cooldown_indicator(self, screen, x, y, current_cooldown, max_cooldown, color):
        """绘制攻击冷却指示器
        
        Args:
            screen: 屏幕对象
            x: 指示器x坐标
            y: 指示器y坐标
            current_cooldown: 当前冷却时间
            max_cooldown: 最大冷却时间
            color: 指示器颜色
        """
        # 计算冷却比例
        cooldown_percent = current_cooldown / max_cooldown
        
        # 绘制冷却文本
        cooldown_text = render_text(f"攻击冷却: {current_cooldown:.1f}秒", 16, color)
        screen.blit(cooldown_text, (x, y))
        
        # 绘制冷却条
        bar_width = 150
        bar_height = 8
        border_rect = pygame.Rect(x, y + 20, bar_width, bar_height)
        pygame.draw.rect(screen, (50, 50, 50), border_rect)
        
        # 绘制冷却进度
        fill_width = int(bar_width * cooldown_percent)
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y + 20, fill_width, bar_height)
            pygame.draw.rect(screen, color, fill_rect)
    
    def _draw_round_result(self, screen):
        """绘制回合结果
        
        Args:
            screen: 屏幕对象
        """
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # 结果文本
        if self.ai_vs_ai_mode:
            if self.winner == self.player1:
                result_text = "AI 1胜利！"
            elif self.winner == self.player2:
                result_text = "AI 2胜利！"
            else:
                result_text = "平局！"
        else:
            if self.winner == self.player1:
                result_text = "玩家1胜利！"
            elif self.winner == self.player2:
                result_text = "玩家2胜利！" if not self.vsai_mode else "AI胜利！"
            else:
                result_text = "平局！"
        
        # 渲染文本
        text_surf = render_text(result_text, 72, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text_surf, text_rect)
        
        # 提示按ESC返回
        hint_text = render_text("按ESC返回主菜单", 36, YELLOW)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(hint_text, hint_rect)
    
    def _check_attack_effects(self, attacker, defender, last_state, last_health):
        """检查攻击和受击，创建相应的视觉特效
        
        Args:
            attacker: 攻击者
            defender: 防御者
            last_state: 攻击者上一帧的状态
            last_health: 防御者上一帧的生命值
        """
        from src.characters.character import CharacterState
        
        # 限制同时存在的特效数量
        if len(self.effects) > 8:  # 限制特效数量
            return
        
        # 检查攻击特效 - 优化攻击特效的触发时机
        if attacker.state in [CharacterState.LIGHT_PUNCH, CharacterState.HEAVY_PUNCH, 
                             CharacterState.LIGHT_KICK, CharacterState.HEAVY_KICK]:
            
            # 获取攻击动作窗口
            attack_window = None
            if hasattr(attacker, 'attack_windows') and attacker.state in attacker.attack_windows:
                attack_window = attacker.attack_windows[attacker.state]
                
            # 计算攻击动画进度
            attack_progress = None
            if hasattr(attacker, 'attack_timer') and hasattr(attacker, 'attack_duration'):
                if attacker.attack_duration > 0:
                    attack_progress = attacker.attack_timer / attacker.attack_duration
                    
            # 检查是否在攻击特效触发窗口内
            should_create_effect = attacker.state != last_state  # 默认状态变化时触发
            
            # 如果有攻击窗口配置，则在窗口开始时创建特效
            if attack_window and attack_progress is not None:
                window_start, _ = attack_window
                # 在攻击窗口开始时创建特效
                if abs(attack_progress - window_start) < 0.05:  # 允许0.05的误差
                    should_create_effect = True
                
            if should_create_effect:
                # 确定特效位置（根据攻击者朝向和位置）
                from src.characters.character import Direction
                if attacker.direction == Direction.RIGHT:
                    effect_x = attacker.x + attacker.width + 5  # 调整位置
                else:
                    effect_x = attacker.x - 35  # 调整位置
                
                effect_y = attacker.y + 50  # 大约在角色的胸部位置
                
                # 创建攻击特效 - 确保不重复创建
                attack_id = f"{attacker.name}_{attacker.state.name.lower()}_{time.time():.2f}"
                if attack_id not in self.damage_created_this_frame:
                    # 创建攻击特效
                    if "punch" in attacker.state.name.lower():
                        self._create_punch_effect(effect_x, effect_y, attacker.state.name.lower())
                    elif "kick" in attacker.state.name.lower():
                        self._create_kick_effect(effect_x, effect_y, attacker.state.name.lower())
                    
                    self.damage_created_this_frame.add(attack_id)
        
        # 检查攻击是否命中（血量减少）
        if defender.health < last_health:  # 生命值减少，表示被击中
            # 计算血量变化
            damage = last_health - defender.health
            current_time = time.time()
            
            # 仍然记录伤害ID，用于防止重复处理
            damage_id = f"{defender.name}_{damage}_{int(current_time*10)}"
            
            # 记录最后一次伤害时间和伤害ID（仍然保留此机制以维护游戏逻辑）
            self.last_damage_time[defender.name] = current_time
            self.active_damage_ids.add(damage_id)
            self.damage_created_this_frame.add(damage_id)
            
    def _create_punch_effect(self, x, y, attack_type):
        """创建拳击特效 - 优化视觉效果
        
        Args:
            x: 特效x坐标
            y: 特效y坐标
            attack_type: 攻击类型
        """
        # 拳击特效是一个快速扩大然后消失的圆形加上冲击波
        is_heavy = "heavy" in attack_type
        
        # 增强颜色对比度和亮度
        if is_heavy:
            color = (255, 140, 0, 230)  # 亮橙色，更高不透明度
        else:
            color = (255, 255, 0, 210)  # 亮黄色，更高不透明度
            
        size = 18 if is_heavy else 12  # 增大初始尺寸
        duration = 0.35 if is_heavy else 0.25  # 增加持续时间提高可见性
        
        # 主要冲击圆 - 使用填充圆增强视觉效果
        self.effects.append({
            "type": "circle",
            "x": x,
            "y": y,
            "color": color,
            "size": size,
            "max_size": size * (5 if is_heavy else 3.5),  # 扩大最大尺寸
            "current_size": size,
            "duration": duration,
            "time_left": duration,
            "filled": True  # 设置为填充圆增强视觉效果
        })
        
        # 添加外轮廓圆增强视觉效果
        self.effects.append({
            "type": "circle",
            "x": x,
            "y": y,
            "color": (255, 255, 255, 150),  # 白色轮廓
            "size": size + 2,
            "max_size": (size + 2) * (5 if is_heavy else 3.5),
            "current_size": size + 2,
            "duration": duration * 0.9,
            "time_left": duration * 0.9
        })
        
        # 添加冲击线效果 - 重拳和轻拳都添加但样式不同
        lines_count = 8 if is_heavy else 4
        for i in range(lines_count):
            angle = i * (360 / lines_count)
            self.effects.append({
                "type": "impact_line",
                "x": x,
                "y": y,
                "color": (255, 255, 255, 200) if is_heavy else (255, 255, 150, 180),
                "angle": angle,
                "length": 10,
                "max_length": 50 if is_heavy else 30,  # 增大冲击线长度
                "current_length": 10,
                "width": 3 if is_heavy else 2,
                "duration": duration * 0.7,
                "time_left": duration * 0.7
            })
    
    def _create_kick_effect(self, x, y, attack_type):
        """创建踢腿特效 - 优化视觉效果
        
        Args:
            x: 特效x坐标
            y: 特效y坐标
            attack_type: 攻击类型
        """
        # 踢腿特效是一个弧形扫过的效果加上冲击粒子
        is_heavy = "heavy" in attack_type
        
        # 增强颜色对比度
        if is_heavy:
            color = (255, 0, 0, 220)  # 更鲜艳的红色
        else:
            color = (0, 200, 255, 200)  # 更亮的青色
            
        size = 28 if is_heavy else 22  # 增大尺寸
        duration = 0.4 if is_heavy else 0.3  # 增加持续时间
        
        # 弧形轨迹 - 更明显的弧线效果
        self.effects.append({
            "type": "arc",
            "x": x,
            "y": y,
            "color": color,
            "radius": size * 2,
            "start_angle": 0,
            "end_angle": 0,
            "max_angle": 180 if is_heavy else 150,  # 增大弧度
            "width": 8 if is_heavy else 5,  # 增加线条宽度
            "duration": duration,
            "time_left": duration
        })
        
        # 添加粒子效果 - 散开的小圆点，增加数量和尺寸
        particle_count = 8 if is_heavy else 5
        for i in range(particle_count):
            angle = i * (360 / particle_count)
            distance = size * 1.5
            particle_x = x + distance * math.cos(angle * (math.pi / 180))
            particle_y = y + distance * math.sin(angle * (math.pi / 180))
            self.effects.append({
                "type": "particle",
                "x": particle_x,
                "y": particle_y,
                "velocity_x": math.cos(angle * (math.pi / 180)) * (4 if is_heavy else 3),  # 增加速度
                "velocity_y": math.sin(angle * (math.pi / 180)) * (4 if is_heavy else 3),
                "color": (*color[:3], 240),  # 提高不透明度
                "size": 7 if is_heavy else 5,  # 增大粒子尺寸
                "duration": duration * 0.9,
                "time_left": duration * 0.9
            })
            
        # 为重踢添加扇形区域效果
        if is_heavy:
            # 添加扇形区域指示攻击范围
            sweep_angle = 120  # 扇形覆盖角度
            start_angle = -60  # 起始角度（相对于水平线）
            
            self.effects.append({
                "type": "arc",
                "x": x,
                "y": y,
                "color": (255, 0, 0, 80),  # 半透明红色
                "radius": size * 4,
                "start_angle": start_angle,
                "end_angle": start_angle,
                "max_angle": sweep_angle,
                "width": size * 4,  # 使用较大宽度模拟扇形
                "duration": duration * 0.6,
                "time_left": duration * 0.6
            })
    
    def _update_effects(self, dt):
        """更新所有特效
        
        Args:
            dt: 时间增量（秒）
        """
        # 如果特效过多，快速清理
        if len(self.effects) > 8:
            self.effects = self.effects[-5:]  # 只保留最新的5个特效
        
        # 更新所有特效，移除已过期或过旧的特效
        current_time = time.time()
        active_damage_ids_to_remove = set()
        
        # 清理任何超过0.8秒的特效（减少存活时间）
        for effect in self.effects[:]:
            if 'creation_time' in effect and current_time - effect.get('creation_time', current_time) > 0.8:
                if "damage_id" in effect:
                    active_damage_ids_to_remove.add(effect["damage_id"])
                self.effects.remove(effect)
        
        # 从活跃ID集合中移除过期的ID
        self.active_damage_ids -= active_damage_ids_to_remove
        
        # 更新所有特效，移除已过期的特效
        for effect in self.effects[:]:  # 创建副本以便在迭代时修改
            effect["time_left"] -= dt
            
            if effect["time_left"] <= 0:
                # 如果特效有damage_id，从活跃ID集合中移除其ID
                if "damage_id" in effect:
                    active_damage_ids_to_remove.add(effect["damage_id"])
                self.effects.remove(effect)
                continue
            
            # 处理延迟效果
            if "delay" in effect and effect["time_left"] > effect["duration"]:
                continue
            
            # 根据特效类型更新参数
            progress = 1 - (effect["time_left"] / effect["duration"])  # 0到1的进度
            
            # 简化特效更新逻辑，根据特效类型进行更新
            if effect["type"] == "circle":
                # 圆形特效逐渐扩大
                effect["current_size"] = effect["size"] + (effect["max_size"] - effect["size"]) * progress
                # 随着时间推移透明度降低
                effect["color"] = (*effect["color"][:3], int(effect["color"][3] * (1 - progress * 0.8)))
                
            elif effect["type"] == "arc":
                # 弧形特效角度逐渐增加
                effect["end_angle"] = effect["max_angle"] * progress
                # 透明度变化
                effect["color"] = (*effect["color"][:3], int(effect["color"][3] * (1 - progress * 0.7)))
                
            elif effect["type"] == "impact_line":
                # 冲击线逐渐延长
                effect["current_length"] = effect["length"] + (effect["max_length"] - effect["length"]) * progress
                # 透明度变化
                effect["color"] = (*effect["color"][:3], int(effect["color"][3] * (1 - progress * 0.9)))
            
            elif effect["type"] in ["particle", "blood_particle"]:
                # 更新粒子位置
                effect["x"] += effect["velocity_x"]
                effect["y"] += effect["velocity_y"]
                if effect["type"] == "blood_particle":
                    effect["velocity_y"] += effect["gravity"]
                # 透明度变化 - 加快衰减
                effect["color"] = (*effect["color"][:3], int(effect["color"][3] * (1 - progress * 1.1)))
            
            elif effect["type"] == "text":
                # 文字特效上升
                effect["offset_y"] = effect["max_offset"] * progress
                # 透明度变化 - 加快衰减
                if progress < 0.1:
                    alpha = 255  # 前10%时间保持完全不透明
                else:
                    alpha = 255 * (1 - ((progress - 0.1) / 0.9))  # 后90%时间逐渐淡出
                effect["color"] = (*effect["color"][:3], int(alpha))
                
        # 从活跃ID集合中移除过期的ID
        self.active_damage_ids -= active_damage_ids_to_remove
    
    def _render_effects(self, screen):
        """渲染所有特效
        
        Args:
            screen: 屏幕对象
        """
        # 如果没有特效，直接返回
        if not self.effects:
            return
            
        # 创建一个透明的Surface用于绘制特效
        effect_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # 先按类型分组，确保正确的渲染顺序
        circle_effects = []
        arc_effects = []
        line_effects = []
        particle_effects = []
        text_effects = []
        
        for effect in self.effects:
            if effect["type"] == "circle":
                circle_effects.append(effect)
            elif effect["type"] == "arc":
                arc_effects.append(effect)
            elif effect["type"] == "impact_line":
                line_effects.append(effect)
            elif effect["type"] in ["particle", "blood_particle"]:
                particle_effects.append(effect)
            elif effect["type"] == "text":
                text_effects.append(effect)
        
        # 渲染圆形特效
        for effect in circle_effects:
            if effect.get("delay", 0) > 0 and effect["time_left"] > effect["duration"]:
                continue  # 跳过延迟效果
                
            pygame.draw.circle(
                effect_surface,
                effect["color"],
                (int(effect["x"]), int(effect["y"])),
                int(effect["current_size"]),
                0 if effect.get("filled", False) else 2
            )
        
        # 渲染弧形特效
        for effect in arc_effects:
            if effect.get("delay", 0) > 0 and effect["time_left"] > effect["duration"]:
                continue
                
            start_angle = math.radians(effect.get("start_angle", 0))
            end_angle = math.radians(effect.get("end_angle", 90))
            pygame.draw.arc(
                effect_surface,
                effect["color"],
                (int(effect["x"] - effect["radius"]), int(effect["y"] - effect["radius"]),
                 int(effect["radius"] * 2), int(effect["radius"] * 2)),
                start_angle,
                end_angle,
                effect.get("width", 2)
            )
        
        # 渲染冲击线特效
        for effect in line_effects:
            if effect.get("delay", 0) > 0 and effect["time_left"] > effect["duration"]:
                continue
                
            angle_rad = math.radians(effect["angle"])
            end_x = effect["x"] + effect["current_length"] * math.cos(angle_rad)
            end_y = effect["y"] + effect["current_length"] * math.sin(angle_rad)
            pygame.draw.line(
                effect_surface,
                effect["color"],
                (int(effect["x"]), int(effect["y"])),
                (int(end_x), int(end_y)),
                effect.get("width", 2)
            )
        
        # 渲染粒子特效
        for effect in particle_effects:
            if effect.get("delay", 0) > 0 and effect["time_left"] > effect["duration"]:
                continue
                
            # 简单粒子就是小圆
            pygame.draw.circle(
                effect_surface,
                effect["color"],
                (int(effect["x"]), int(effect["y"])),
                effect["size"]
            )
        
        # 最后绘制所有文本特效
        for effect in text_effects:
            if effect["type"] == "text":
                # 普通文本特效
                font = pygame.font.SysFont(None, effect["size"])
                text_surf = font.render(effect["text"], True, effect["color"])
                text_rect = text_surf.get_rect(center=(int(effect["x"]), int(effect["y"] + effect["offset_y"])))
                
                # 添加简单的文本阴影增强可读性
                shadow_surf = font.render(effect["text"], True, (0, 0, 0, effect["color"][3] // 2))
                shadow_rect = shadow_surf.get_rect(center=(int(effect["x"]) + 2, int(effect["y"] + effect["offset_y"]) + 2))
                effect_surface.blit(shadow_surf, shadow_rect)
                
                effect_surface.blit(text_surf, text_rect)
        
        # 将特效Surface绘制到屏幕上
        screen.blit(effect_surface, (0, 0))
        
    def _clean_effects(self):
        """清理过期的特效"""
        # 记录当前时间，用于删除过时的特效
        current_time = time.time()
        effects_to_remove = []
        active_damage_ids_to_remove = set()
        
        # 按创建时间排序，保留最新的特效
        effects_with_time = []
        
        # 为每个特效添加创建时间（如果没有）
        for i, effect in enumerate(self.effects):
            if 'creation_time' not in effect:
                self.effects[i]['creation_time'] = current_time
            
            effects_with_time.append((effect, effect.get('creation_time', current_time)))
        
        # 按创建时间排序
        effects_with_time.sort(key=lambda x: x[1], reverse=True)  # 最新的在前面
        
        # 保留最新的5个特效，进一步提高流畅性
        if len(effects_with_time) > 5:
            effects_to_keep = [item[0] for item in effects_with_time[:5]]
            
            # 找出要删除的特效
            for effect in self.effects:
                if effect not in effects_to_keep:
                    effects_to_remove.append(effect)
                    # 如果要删除的特效有damage_id，也从活跃ID集合中移除
                    if "damage_id" in effect:
                        active_damage_ids_to_remove.add(effect["damage_id"])
        
        # 移除标记的特效
        for effect in effects_to_remove:
            if effect in self.effects:
                self.effects.remove(effect)
        
        # 从活跃ID集合中移除已删除特效的ID
        self.active_damage_ids -= active_damage_ids_to_remove