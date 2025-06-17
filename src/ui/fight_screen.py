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
        
        # 检测攻击和受击，创建视觉特效
        self._check_attack_effects(self.player1, self.player2, self.p1_last_state, self.p1_last_health)
        self._check_attack_effects(self.player2, self.player1, self.p2_last_state, self.p2_last_health)
        
        # 更新特效
        self._update_effects(dt)
        
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
        
        # 绘制玩家名称
        if self.ai_vs_ai_mode:
            p1_name = render_text("AI 1", 36, BLUE)
            p2_name = render_text("AI 2", 36, RED)
            
            # 在AI名称下方显示行为模式
            if self.ai1_controller:
                behavior1_text = render_text("(进攻型)", 16, BLUE)
                screen.blit(behavior1_text, (50, 60))
            if self.ai_controller:
                behavior2_text = render_text("(防守型)", 16, RED)
                screen.blit(behavior2_text, (SCREEN_WIDTH - 350, 60))
                
            # 在顶部添加模式标题
            mode_text = render_text("AI对战AI模式", 24, YELLOW)
            mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
            screen.blit(mode_text, mode_rect)
        else:
            p1_name = render_text("玩家1", 36, BLUE)
            p2_name = render_text("玩家2" if not self.vsai_mode else "AI", 36, RED)
        
        screen.blit(p1_name, (50, 20))
        screen.blit(p2_name, (SCREEN_WIDTH - 350, 20))
        
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
        
        # 限制同时存在的特效数量，如果特效太多，不再创建新特效
        if len(self.effects) > 25:  # 降低特效数量限制（原为50）
            return
        
        # 检查攻击特效
        if attacker.state in [CharacterState.LIGHT_PUNCH, CharacterState.HEAVY_PUNCH, 
                             CharacterState.LIGHT_KICK, CharacterState.HEAVY_KICK]:
            if attacker.state != last_state:  # 状态刚刚变化，创建攻击特效
                attack_type = attacker.state.name.lower()
                
                # 确定特效位置（根据攻击者朝向和位置）
                from src.characters.character import Direction
                if attacker.direction == Direction.RIGHT:
                    effect_x = attacker.x + attacker.width
                else:
                    effect_x = attacker.x - 30
                
                effect_y = attacker.y + 50  # 大约在角色的胸部位置
                
                # 创建攻击特效
                if "punch" in attack_type:
                    self._create_punch_effect(effect_x, effect_y, attack_type)
                elif "kick" in attack_type:
                    self._create_kick_effect(effect_x, effect_y, attack_type)
        
        # 检查受击特效和血量变化
        if defender.health < last_health:  # 生命值减少，表示被击中
            # 计算血量变化
            damage = last_health - defender.health
            
            # 在被击中的位置创建受击特效
            hit_x = defender.x + defender.width // 2
            hit_y = defender.y + defender.height // 2
            self._create_hit_effect(hit_x, hit_y)
            
            # 在头顶创建血量变化显示
            self._create_damage_text(defender.x + defender.width // 2, defender.y, damage)
    
    def _create_punch_effect(self, x, y, attack_type):
        """创建拳击特效
        
        Args:
            x: 特效x坐标
            y: 特效y坐标
            attack_type: 攻击类型
        """
        # 拳击特效是一个快速扩大然后消失的圆形加上冲击波
        is_heavy = "heavy" in attack_type
        color = self.effect_colors.get(attack_type, (255, 255, 0, 180))
        size = 15 if is_heavy else 10
        duration = 0.3 if is_heavy else 0.2
        
        # 主要冲击圆
        self.effects.append({
            "type": "circle",
            "x": x,
            "y": y,
            "color": color,
            "size": size,
            "max_size": size * (4 if is_heavy else 3),
            "current_size": size,
            "duration": duration,
            "time_left": duration
        })
        
        # 添加冲击线效果 - 重拳特有
        if is_heavy:
            for i in range(6):  # 6条冲击线
                angle = i * (360 / 6)
                self.effects.append({
                    "type": "impact_line",
                    "x": x,
                    "y": y,
                    "color": color,
                    "angle": angle,
                    "length": 10,
                    "max_length": 40,
                    "current_length": 10,
                    "width": 3,
                    "duration": duration * 0.8,
                    "time_left": duration * 0.8
                })
        
        # 添加文字特效
        text = "重拳!" if is_heavy else "拳!"
        self.effects.append({
            "type": "text",
            "x": x + 20,
            "y": y - 20,
            "text": text,
            "size": 24 if is_heavy else 20,
            "color": (255, 255, 255, 255),
            "duration": duration * 1.5,
            "time_left": duration * 1.5,
            "offset_y": 0,
            "max_offset": -30
        })
    
    def _create_kick_effect(self, x, y, attack_type):
        """创建踢腿特效
        
        Args:
            x: 特效x坐标
            y: 特效y坐标
            attack_type: 攻击类型
        """
        # 踢腿特效是一个弧形扫过的效果加上冲击粒子
        is_heavy = "heavy" in attack_type
        color = self.effect_colors.get(attack_type, (0, 255, 255, 180))
        size = 25 if is_heavy else 20
        duration = 0.35 if is_heavy else 0.25
        
        # 弧形轨迹
        self.effects.append({
            "type": "arc",
            "x": x,
            "y": y,
            "color": color,
            "radius": size * 2,
            "start_angle": 0,
            "end_angle": 0,
            "max_angle": 150 if is_heavy else 120,
            "width": 6 if is_heavy else 4,
            "duration": duration,
            "time_left": duration
        })
        
        # 添加粒子效果 - 散开的小圆点
        for i in range(8 if is_heavy else 5):
            angle = i * (360 / (8 if is_heavy else 5))
            distance = size * 1.5
            particle_x = x + distance * math.cos(angle * (math.pi / 180))
            particle_y = y + distance * math.sin(angle * (math.pi / 180))
            self.effects.append({
                "type": "particle",
                "x": particle_x,
                "y": particle_y,
                "velocity_x": math.cos(angle * (math.pi / 180)) * (3 if is_heavy else 2),
                "velocity_y": math.sin(angle * (math.pi / 180)) * (3 if is_heavy else 2),
                "color": (*color[:3], 220),
                "size": 5 if is_heavy else 3,
                "duration": duration * 0.8,
                "time_left": duration * 0.8
            })
        
        # 添加文字特效
        text = "重踢!" if is_heavy else "踢!"
        self.effects.append({
            "type": "text",
            "x": x + 20,
            "y": y - 20,
            "text": text,
            "size": 24 if is_heavy else 20,
            "color": (255, 255, 255, 255),
            "duration": duration * 1.5,
            "time_left": duration * 1.5,
            "offset_y": 0,
            "max_offset": -30
        })
    
    def _create_hit_effect(self, x, y):
        """创建受击特效
        
        Args:
            x: 特效x坐标
            y: 特效y坐标
        """
        # 受击特效是爆炸星形和冲击波
        color = self.effect_colors["hit"]
        duration = 0.4
        
        # 主星形爆炸
        self.effects.append({
            "type": "hit",
            "x": x,
            "y": y,
            "color": color,
            "size": 20,
            "duration": duration,
            "time_left": duration,
            "lines": 10  # 增加星形的线数
        })
        
        # 添加冲击波圆圈
        self.effects.append({
            "type": "circle",
            "x": x,
            "y": y,
            "color": (255, 255, 255, 180),
            "size": 10,
            "max_size": 40,
            "current_size": 10,
            "duration": duration * 0.8,
            "time_left": duration * 0.8
        })
        
        # 添加多个小爆炸粒子
        for i in range(6):
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            delay = random.uniform(0, 0.2)
            particle_duration = random.uniform(0.2, 0.3)
            self.effects.append({
                "type": "mini_explosion",
                "x": x + offset_x,
                "y": y + offset_y,
                "color": (255, 200, 100, 200),
                "size": random.randint(5, 10),
                "duration": particle_duration,
                "time_left": particle_duration + delay,
                "delay": delay
            })
        
        # 添加"啪!"文字效果
        self.effects.append({
            "type": "text",
            "x": x,
            "y": y - 30,
            "text": "啪!",
            "size": 28,
            "color": (255, 0, 0, 255),
            "duration": duration * 1.5,
            "time_left": duration * 1.5,
            "offset_y": 0,
            "max_offset": -20
        })
    
    def _create_damage_text(self, x, y, damage):
        """创建血量变化文本特效
        
        Args:
            x: 文本x坐标
            y: 文本y坐标
            damage: 伤害值
        """
        # 如果伤害显示特效已经太多，限制新特效的创建
        damage_texts = [e for e in self.effects if e["type"] == "damage_text"]
        if len(damage_texts) >= 3:  # 限制最多同时显示3个伤害文本
            return
            
        # 创建伤害文本特效
        duration = 0.5  # 大幅减少持续时间（原为0.8）
        
        # 根据伤害大小调整文本大小和颜色
        if damage >= 8:  # 重伤害
            size = 32
            color = (255, 0, 0, 255)  # 鲜红色
        elif damage >= 5:  # 中伤害
            size = 28
            color = (255, 100, 0, 255)  # 橙红色
        else:  # 轻伤害
            size = 24
            color = (255, 200, 0, 255)  # 黄色
        
        # 添加到特效系统
        self.effects.append({
            "type": "damage_text",
            "x": x,
            "y": y - 30,  # 头顶上方
            "text": f"-{damage}",
            "size": size,
            "color": color,
            "duration": duration,
            "time_left": duration,
            "offset_y": 0,
            "max_offset": -30  # 再次减少漂浮距离（原为-40）
        })
        
        # 大幅减少血溅效果粒子数量
        max_particles = min(3, int(damage/2))  # 最多3个粒子，每2点伤害1个粒子
        for i in range(max_particles):
            angle = random.uniform(0, 360)
            speed = random.uniform(0.8, 1.5)  # 进一步降低速度范围（原为1-2）
            size = random.uniform(1.5, 2.5)  # 进一步降低大小范围（原为2-3）
            self.effects.append({
                "type": "blood_particle",
                "x": x,
                "y": y - 20,
                "velocity_x": math.cos(angle * (math.pi / 180)) * speed,
                "velocity_y": math.sin(angle * (math.pi / 180)) * speed - 1.0,  # 降低初始向上速度（原为-1.5）
                "color": (255, 0, 0, 200),
                "size": size,
                "duration": 0.3,  # 减少持续时间（原为0.5）
                "time_left": 0.3,
                "gravity": 0.1
            })
    
    def _update_effects(self, dt):
        """更新所有特效
        
        Args:
            dt: 时间增量（秒）
        """
        # 如果特效过多，强制移除一些最老的特效
        if len(self.effects) > 40:  # 降低特效上限（原为100）
            # 保留最新的20个特效，删除其他的（原为50）
            self.effects = self.effects[-20:]
        
        # 更新所有特效，移除已过期的特效
        for effect in self.effects[:]:  # 创建副本以便在迭代时修改
            effect["time_left"] -= dt
            
            if effect["time_left"] <= 0:
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
                effect["color"] = (*effect["color"][:3], int(effect["color"][3] * (1 - progress)))
                
            elif effect["type"] == "arc":
                # 弧形特效角度逐渐增加
                effect["end_angle"] = effect["max_angle"] * progress
                # 透明度变化
                effect["color"] = (*effect["color"][:3], int(effect["color"][3] * (1 - progress * 0.5)))
                
            elif effect["type"] == "hit":
                # 受击特效大小先增加后减小
                if progress < 0.5:
                    effect["size"] = 20 + 30 * (progress * 2)  # 增加最大尺寸
                else:
                    effect["size"] = 50 - 50 * ((progress - 0.5) * 2)
                # 透明度变化
                effect["color"] = (*effect["color"][:3], int(effect["color"][3] * (1 - progress * 0.7)))
            
            elif effect["type"] == "impact_line":
                # 冲击线逐渐延长
                effect["current_length"] = effect["length"] + (effect["max_length"] - effect["length"]) * progress
                # 透明度变化
                effect["color"] = (*effect["color"][:3], int(effect["color"][3] * (1 - progress)))
            
            elif effect["type"] in ["particle", "blood_particle"]:
                # 更新粒子位置
                effect["x"] += effect["velocity_x"]
                effect["y"] += effect["velocity_y"]
                if effect["type"] == "blood_particle":
                    effect["velocity_y"] += effect["gravity"]
                # 透明度变化
                effect["color"] = (*effect["color"][:3], int(effect["color"][3] * (1 - progress)))
            
            elif effect["type"] in ["text", "damage_text"]:
                # 文字特效上升
                effect["offset_y"] = effect["max_offset"] * progress
                # 透明度变化
                if progress < 0.2:
                    alpha = 255  # 前20%时间保持完全不透明
                else:
                    alpha = 255 * (1 - ((progress - 0.2) / 0.8))  # 后80%时间逐渐淡出
                effect["color"] = (*effect["color"][:3], int(alpha))
    
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
        
        # 对特效进行分组处理，减少渲染次数
        particle_effects = []
        text_effects = []
        other_effects = []
        
        for effect in self.effects:
            # 跳过延迟中的效果
            if "delay" in effect and effect["time_left"] > effect["duration"]:
                continue
                
            # 按类型分组
            if effect["type"] in ["particle", "blood_particle"]:
                particle_effects.append(effect)
            elif effect["type"] in ["text", "damage_text"]:
                text_effects.append(effect)
            else:
                other_effects.append(effect)
        
        # 先绘制非粒子和文本特效
        for effect in other_effects:
            if effect["type"] == "circle":
                pygame.draw.circle(effect_surface, effect["color"], 
                                  (int(effect["x"]), int(effect["y"])), 
                                  int(effect["current_size"]))
                
            elif effect["type"] == "arc":
                # 弧形特效
                pygame.draw.arc(effect_surface, effect["color"],
                               (effect["x"] - effect["radius"], effect["y"] - effect["radius"],
                                effect["radius"] * 2, effect["radius"] * 2),
                               effect["start_angle"] * (math.pi / 180),  # 转换为弧度
                               effect["end_angle"] * (math.pi / 180),
                               effect["width"])
                
            elif effect["type"] == "hit":
                # 受击特效（星形）
                center = (int(effect["x"]), int(effect["y"]))
                size = int(effect["size"])
                lines = effect["lines"]
                
                for i in range(lines):
                    angle = (360 / lines) * i
                    rad = angle * (math.pi / 180)
                    end_x = center[0] + int(size * 1.5 * math.cos(rad))
                    end_y = center[1] + int(size * 1.5 * math.sin(rad))
                    pygame.draw.line(effect_surface, effect["color"], center, (end_x, end_y), 3)
                
                # 添加中心圆
                pygame.draw.circle(effect_surface, effect["color"], center, size // 2)
            
            elif effect["type"] == "impact_line":
                # 冲击线效果
                start_x, start_y = effect["x"], effect["y"]
                angle_rad = effect["angle"] * (math.pi / 180)
                end_x = start_x + effect["current_length"] * math.cos(angle_rad)
                end_y = start_y + effect["current_length"] * math.sin(angle_rad)
                
                pygame.draw.line(effect_surface, effect["color"], 
                                (int(start_x), int(start_y)), 
                                (int(end_x), int(end_y)), 
                                effect["width"])
        
        # 绘制所有粒子特效
        for effect in particle_effects:
            pygame.draw.circle(effect_surface, effect["color"], 
                              (int(effect["x"]), int(effect["y"])), 
                              int(effect["size"]))
        
        # 最后绘制所有文本特效
        for effect in text_effects:
            if effect["type"] == "text":
                # 普通文本特效
                font = pygame.font.SysFont(None, effect["size"])
                text_surf = font.render(effect["text"], True, effect["color"])
                text_rect = text_surf.get_rect(center=(effect["x"], effect["y"] + effect["offset_y"]))
                effect_surface.blit(text_surf, text_rect)
            elif effect["type"] == "damage_text":
                # 伤害文本特效
                text = effect["text"]
                size = effect["size"]
                color = effect["color"]
                text_surf = render_text(text, size, color)
                text_rect = text_surf.get_rect(center=(effect["x"], effect["y"] + effect["offset_y"]))
                
                # 简化描边，只使用一个背景
                shadow_surf = render_text(text, size, (0, 0, 0, color[3] // 2))
                shadow_rect = shadow_surf.get_rect(center=(effect["x"] + 2, effect["y"] + effect["offset_y"] + 2))
                effect_surface.blit(shadow_surf, shadow_rect)
                
                effect_surface.blit(text_surf, text_rect)
        
        # 将特效Surface绘制到屏幕上
        screen.blit(effect_surface, (0, 0))