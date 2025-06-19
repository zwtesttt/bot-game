#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import math
from enum import Enum
from src.engine.config import (
    CHARACTER_WIDTH, CHARACTER_HEIGHT, GRAVITY, JUMP_FORCE,
    WALK_SPEED, RUN_SPEED, MAX_HEALTH
)

class CharacterState(Enum):
    """角色状态枚举"""
    IDLE = 0
    WALKING = 1
    RUNNING = 2
    JUMPING = 3
    FALLING = 4
    CROUCHING = 5
    LIGHT_PUNCH = 6
    HEAVY_PUNCH = 7
    LIGHT_KICK = 8
    HEAVY_KICK = 9
    BLOCKING = 10
    HIT = 11
    DEFEATED = 12

class Direction(Enum):
    """角色朝向枚举"""
    RIGHT = 0
    LEFT = 1

class Character(pygame.sprite.Sprite):
    """角色基类"""
    
    def __init__(self, x, y, name):
        """初始化角色"""
        super().__init__()
        self.name = name
        self.width = CHARACTER_WIDTH
        self.height = CHARACTER_HEIGHT
        
        # 位置和物理属性
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.is_jumping = False
        self.is_crouching = False
        self.is_blocking = False
        
        # 生命值和状态
        self.health = MAX_HEALTH
        self.state = CharacterState.IDLE
        self.direction = Direction.RIGHT
        self.animation_frame = 0
        self.animation_speed = 0.2  # 基本动画速度
        self.animation_timer = 0
        
        # 攻击动画速度 - 调整攻击动画时间以提高流畅度
        self.attack_animation_speeds = {
            CharacterState.LIGHT_PUNCH: 0.13,  # 轻拳动画更快
            CharacterState.HEAVY_PUNCH: 0.16,  # 重拳动画适中
            CharacterState.LIGHT_KICK: 0.13,   # 轻腿动画更快
            CharacterState.HEAVY_KICK: 0.16    # 重腿动画适中
        }
        
        # 攻击生效窗口 - 添加攻击判定窗口配置
        self.attack_windows = {
            CharacterState.LIGHT_PUNCH: (0.1, 0.2),   # 轻拳攻击判定窗口(开始,结束)
            CharacterState.HEAVY_PUNCH: (0.15, 0.3),  # 重拳攻击判定窗口(开始,结束)
            CharacterState.LIGHT_KICK: (0.1, 0.2),    # 轻腿攻击判定窗口(开始,结束)
            CharacterState.HEAVY_KICK: (0.15, 0.3)    # 重腿攻击判定窗口(开始,结束)
        }
        
        # 受击状态恢复
        self.hit_recovery_timer = 0
        self.hit_stun_duration = 0.45  # 略微减少受击硬直时间，提高流畅度
        
        # 加载图像
        self.sprites = self._load_sprites()
        self.image = self.sprites[self.state][self.direction][0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 攻击属性
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 0
        self.attack_cooldown = 0
        self.attack_cooldown_duration = 0.6  # 原来是0.85，减少了冷却时间
        self.attack_hitbox = pygame.Rect(0, 0, 0, 0)
        self.has_hit_opponent = False  # 标记当前攻击是否已经命中对手
        
        # 攻击伤害配置
        self.attack_damages = {
            CharacterState.LIGHT_PUNCH: 4,  # 原来是2
            CharacterState.HEAVY_PUNCH: 6,  # 原来是3
            CharacterState.LIGHT_KICK: 4,   # 原来是2
            CharacterState.HEAVY_KICK: 8    # 原来是4
        }
        
        # 音效属性（默认为None，子类可以重写）
        self.jump_sound = None
        self.hit_sound = None
        self.punch_sound = None
        self.kick_sound = None
    
    def _load_sprites(self):
        """加载角色精灵图"""
        # 这应该被子类重写
        # 返回格式: {state: {direction: [frames]}}
        return {}
    
    def update(self, dt, opponent):
        """更新角色状态
        
        Args:
            dt: 时间增量（秒）
            opponent: 对手角色
        """
        # 处理受击状态恢复
        if self.state == CharacterState.HIT:
            self.hit_recovery_timer += dt
            if self.hit_recovery_timer >= self.hit_stun_duration:
                self.state = CharacterState.IDLE
                self.hit_recovery_timer = 0
                self.animation_frame = 0
                self.animation_timer = 0
        
        # 更新朝向 - 确保AI角色始终朝向对方
        if hasattr(self, 'name') and self.name.startswith('AI') and not self.is_attacking:
            # 如果是AI角色且没有在攻击中，强制朝向对方
            if self.x < opponent.x:
                self.direction = Direction.RIGHT
            else:
                self.direction = Direction.LEFT
        
        # 处理物理
        self._apply_physics(dt, opponent)
        
        # 更新动画
        self._update_animation(dt)
        
        # 处理攻击逻辑
        if self.is_attacking:
            self._handle_attack(dt, opponent)
        
        # 更新攻击冷却时间
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            if self.attack_cooldown < 0:
                self.attack_cooldown = 0
        
        # 处理角色碰撞
        self._handle_character_collision(opponent)
        
        # 更新rect位置
        self.rect.x = self.x
        self.rect.y = self.y
    
    def _apply_physics(self, dt, opponent=None):
        """应用物理效果
        
        Args:
            dt: 时间增量（秒）
            opponent: 对手角色（可选）
        """
        # 如果角色未被击败
        if self.state != CharacterState.DEFEATED:
            # 应用重力
            if not self.is_on_ground():
                self.vel_y += GRAVITY
                if self.vel_y > 0 and self.state != CharacterState.FALLING:
                    self.state = CharacterState.FALLING
                    # 状态变化时重置动画帧
                    self.animation_frame = 0
                    self.animation_timer = 0
            else:
                # 在地面上且不处于特殊状态时
                if self.state == CharacterState.FALLING:
                    self.vel_y = 0
                    self.is_jumping = False
                    self.state = CharacterState.IDLE
                    # 状态变化时重置动画帧
                    self.animation_frame = 0
                    self.animation_timer = 0
            
            # 保存之前的位置用于碰撞检测
            prev_x = self.x
            
            # 应用水平和垂直速度
            self.x += self.vel_x * dt * 60
            self.y += self.vel_y * dt * 60
            
            # 防止角色超出屏幕底部
            if self.y > 600 - self.height:
                self.y = 600 - self.height
                self.vel_y = 0
                self.is_jumping = False
                if self.state == CharacterState.FALLING:
                    self.state = CharacterState.IDLE
                    # 状态变化时重置动画帧
                    self.animation_frame = 0
                    self.animation_timer = 0
            
            # 防止角色超出屏幕左右边界
            if self.x < 0:
                self.x = 0
                self.vel_x = 0  # 停止水平移动
            elif self.x > 800 - self.width:
                self.x = 800 - self.width
                self.vel_x = 0  # 停止水平移动
    
    def _update_animation(self, dt):
        """更新角色动画"""
        # 根据当前状态选择合适的动画速度
        current_animation_speed = self.animation_speed
        if self.state in self.attack_animation_speeds:
            current_animation_speed = self.attack_animation_speeds[self.state]
            
        self.animation_timer += dt
        if self.animation_timer >= current_animation_speed:
            self.animation_timer = 0
            sprite_list = self.sprites[self.state][self.direction]
            
            # 确保当前帧在有效范围内
            if len(sprite_list) > 0:
                # 对于攻击和受击动画，只播放一次完整的动画序列
                if self.state in [CharacterState.LIGHT_PUNCH, CharacterState.HEAVY_PUNCH,
                                CharacterState.LIGHT_KICK, CharacterState.HEAVY_KICK,
                                CharacterState.HIT]:
                    # 如果是最后一帧，不再增加帧数
                    if self.animation_frame < len(sprite_list) - 1:
                        self.animation_frame += 1
                    # 否则保持在最后一帧，直到状态改变
                    elif self.state == CharacterState.HIT:
                        # HIT状态动画播放完毕后，恢复为IDLE状态
                        self.state = CharacterState.IDLE
                        self.animation_frame = 0
                        self.animation_timer = 0
                else:
                    # 对于其他动画，循环播放
                    self.animation_frame = (self.animation_frame + 1) % len(sprite_list)
                
                self.image = sprite_list[self.animation_frame]
            else:
                # 如果当前状态没有有效帧，回退到IDLE状态
                self.state = CharacterState.IDLE
                self.animation_frame = 0
                if len(self.sprites[self.state][self.direction]) > 0:
                    self.image = self.sprites[self.state][self.direction][0]
    
    def _handle_attack(self, dt, opponent):
        """处理攻击逻辑"""
        self.attack_timer += dt
        if self.attack_timer >= self.attack_duration:
            self.is_attacking = False
            self.attack_timer = 0
            self.has_hit_opponent = False  # 重置命中标记
            self.state = CharacterState.IDLE
            # 设置攻击冷却时间
            self.attack_cooldown = self.attack_cooldown_duration
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
        else:
            # 检测攻击是否命中 - 使用精确的攻击窗口
            if not self.has_hit_opponent and self.state in self.attack_windows:
                # 获取当前攻击类型的判定窗口
                window_start, window_end = self.attack_windows[self.state]
                attack_progress = self.attack_timer / self.attack_duration
                
                # 检查是否在攻击判定窗口内
                if window_start <= attack_progress <= window_end:
                    # 更新攻击判定框
                    self._update_attack_hitbox()
                    
                    # 计算与对手的实际距离
                    distance = abs((self.x + self.width/2) - (opponent.x + opponent.width/2))
                    
                    # 为AI角色增大攻击距离
                    ai_bonus_distance = 0
                    if hasattr(self, 'name') and self.name.startswith('AI'):
                        ai_bonus_distance = 50  # AI角色额外攻击距离
                    
                    max_attack_distance = self.width * 2.0 + ai_bonus_distance  # 保持最大攻击距离
                    
                    # 在AI对战AI模式下打印调试信息
                    if hasattr(self, 'name') and self.name.startswith('AI'):
                        print(f"{self.name} 尝试攻击: 状态={self.state.name}, 距离={distance:.1f}, 最大攻击距离={max_attack_distance}")
                        print(f"判定框情况: {self.attack_hitbox}, 对手位置: {opponent.rect}")
                    
                    # 放宽判定条件，使AI更容易命中对手
                    ai_vs_ai = (hasattr(self, 'name') and self.name.startswith('AI') and 
                                hasattr(opponent, 'name') and opponent.name.startswith('AI'))
                                
                    # AI对战AI时额外放宽判定条件
                    if ai_vs_ai:
                        # 在AI对战AI模式下，如果两个AI都在地面上，总是命中
                        if self.is_on_ground() and opponent.is_on_ground() and distance <= max_attack_distance * 1.2:
                            # 标记已命中
                            self.has_hit_opponent = True
                            
                            # 应用伤害 (从伤害配置表中获取)
                            damage = self.attack_damages.get(self.state, 2)  
                            
                            # 实际应用伤害
                            actual_damage = opponent.take_damage(damage)
                            
                            print(f"{self.name} AI对战模式命中 {opponent.name}! 造成 {actual_damage} 伤害")
                            return
                    
                    # 标准判定逻辑
                    if distance <= max_attack_distance and self.attack_hitbox.colliderect(opponent.rect) and not opponent.is_blocking:
                        # 标记已命中
                        self.has_hit_opponent = True
                        
                        # 应用伤害 (从伤害配置表中获取)
                        damage = self.attack_damages.get(self.state, 2)
                        
                        # 实际应用伤害
                        actual_damage = opponent.take_damage(damage)
                        
                        # 打印命中信息
                        if hasattr(self, 'name'):
                            print(f"{self.name} 命中 {opponent.name}! 造成 {actual_damage} 伤害")
                            
                    elif distance > max_attack_distance and hasattr(self, 'name'):
                        # 距离太远，无法命中
                        print(f"{self.name} 攻击未命中 - 距离太远: {distance:.1f} > {max_attack_distance}")
                    elif not self.attack_hitbox.colliderect(opponent.rect) and hasattr(self, 'name'):
                        # 判定框未重叠
                        print(f"{self.name} 攻击未命中 - 判定框未重叠")
                    elif opponent.is_blocking and hasattr(self, 'name'):
                        # 对手格挡成功
                        print(f"{self.name} 攻击被 {opponent.name} 格挡")
    
    def is_on_ground(self):
        """检查角色是否在地面上"""
        return self.y >= 600 - self.height
    
    def move_left(self):
        """向左移动"""
        if self.state not in [CharacterState.DEFEATED, CharacterState.HIT] and not self.is_attacking:
            self.vel_x = -WALK_SPEED
            self.direction = Direction.LEFT
            if self.is_on_ground() and not self.is_crouching:
                if self.state != CharacterState.WALKING:
                    self.state = CharacterState.WALKING
                    # 只有在状态变化时才重置动画帧
                    self.animation_frame = 0
                    self.animation_timer = 0
    
    def move_right(self):
        """向右移动"""
        if self.state not in [CharacterState.DEFEATED, CharacterState.HIT] and not self.is_attacking:
            self.vel_x = WALK_SPEED
            self.direction = Direction.RIGHT
            if self.is_on_ground() and not self.is_crouching:
                if self.state != CharacterState.WALKING:
                    self.state = CharacterState.WALKING
                    # 只有在状态变化时才重置动画帧
                    self.animation_frame = 0
                    self.animation_timer = 0
    
    def stop_moving(self):
        """停止移动"""
        self.vel_x = 0
        if self.is_on_ground() and self.state == CharacterState.WALKING:
            self.state = CharacterState.IDLE
            # 只有在状态变化时才重置动画帧
            self.animation_frame = 0
            self.animation_timer = 0
    
    def jump(self):
        """跳跃"""
        if self.is_on_ground() and not self.is_jumping and not self.is_attacking:
            self.vel_y = JUMP_FORCE
            self.is_jumping = True
            self.state = CharacterState.JUMPING
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
            # 播放跳跃音效
            if self.jump_sound:
                self.jump_sound.play()
    
    def crouch(self):
        """下蹲"""
        if self.is_on_ground() and not self.is_jumping and not self.is_attacking:
            self.is_crouching = True
            self.state = CharacterState.CROUCHING
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
    
    def stand_up(self):
        """站起"""
        if self.is_crouching:
            self.is_crouching = False
            self.state = CharacterState.IDLE
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
    
    def block(self):
        """格挡"""
        if not self.is_attacking:
            self.is_blocking = True
            self.state = CharacterState.BLOCKING
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
    
    def stop_blocking(self):
        """停止格挡"""
        if self.is_blocking:
            self.is_blocking = False
            self.state = CharacterState.IDLE
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
    
    def light_punch(self):
        """轻拳"""
        if not self.is_attacking and self.attack_cooldown <= 0 and self.state not in [CharacterState.JUMPING, CharacterState.FALLING, CharacterState.DEFEATED]:
            self.is_attacking = True
            self.attack_timer = 0
            self.attack_duration = 0.18  # 原来是0.22，减少了持续时间
            self.state = CharacterState.LIGHT_PUNCH
            self.has_hit_opponent = False  # 重置命中标记
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
            self._update_attack_hitbox()
            # 播放攻击音效
            if self.punch_sound:
                self.punch_sound.play()
    
    def heavy_punch(self):
        """重拳"""
        if not self.is_attacking and self.attack_cooldown <= 0 and self.state not in [CharacterState.JUMPING, CharacterState.FALLING, CharacterState.DEFEATED]:
            self.is_attacking = True
            self.attack_timer = 0
            self.attack_duration = 0.30  # 原来是0.38，减少了持续时间
            self.state = CharacterState.HEAVY_PUNCH
            self.has_hit_opponent = False  # 重置命中标记
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
            self._update_attack_hitbox()
            # 播放攻击音效
            if self.punch_sound:
                self.punch_sound.play()
    
    def light_kick(self):
        """轻腿"""
        if not self.is_attacking and self.attack_cooldown <= 0 and self.state not in [CharacterState.JUMPING, CharacterState.FALLING, CharacterState.DEFEATED]:
            self.is_attacking = True
            self.attack_timer = 0
            self.attack_duration = 0.18  # 原来是0.22，减少了持续时间
            self.state = CharacterState.LIGHT_KICK
            self.has_hit_opponent = False  # 重置命中标记
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
            self._update_attack_hitbox()
            # 播放攻击音效
            if self.kick_sound:
                self.kick_sound.play()
    
    def heavy_kick(self):
        """重腿"""
        if not self.is_attacking and self.attack_cooldown <= 0 and self.state not in [CharacterState.JUMPING, CharacterState.FALLING, CharacterState.DEFEATED]:
            self.is_attacking = True
            self.attack_timer = 0
            self.attack_duration = 0.30  # 原来是0.38，减少了持续时间
            self.state = CharacterState.HEAVY_KICK
            self.has_hit_opponent = False  # 重置命中标记
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
            self._update_attack_hitbox()
            # 播放攻击音效
            if self.kick_sound:
                self.kick_sound.play()
    
    def _update_attack_hitbox(self):
        """更新攻击判定框"""
        # 根据攻击类型调整判定框大小和位置
        attack_width = 0
        attack_height = 0
        attack_offset_x = 0
        attack_offset_y = 0
        
        # 针对不同攻击类型优化判定框
        if self.state == CharacterState.LIGHT_PUNCH:
            attack_width = 80  # 原来是70，增加攻击范围
            attack_height = 50
            attack_offset_y = 35
        elif self.state == CharacterState.HEAVY_PUNCH:
            attack_width = 95  # 原来是85，增加攻击范围
            attack_height = 65
            attack_offset_y = 30
        elif self.state == CharacterState.LIGHT_KICK:
            attack_width = 90  # 原来是80，增加攻击范围
            attack_height = 40
            attack_offset_y = 65
        elif self.state == CharacterState.HEAVY_KICK:
            attack_width = 110  # 原来是100，增加攻击范围
            attack_height = 50
            attack_offset_y = 60
        
        # 修改判定框位置计算逻辑，保持方向一致性
        if self.direction == Direction.RIGHT:
            attack_offset_x = self.width - 10  # 原来是20，增加向右的判定距离
            self.attack_hitbox = pygame.Rect(
                self.x + attack_offset_x, 
                self.y + attack_offset_y, 
                attack_width, 
                attack_height
            )
        else:  # 向左方向
            attack_offset_x = -attack_width + 10  # 原来是20，增加向左的判定距离
            self.attack_hitbox = pygame.Rect(
                self.x + attack_offset_x, 
                self.y + attack_offset_y, 
                attack_width, 
                attack_height
            )
    
    def take_damage(self, damage):
        """受到伤害"""
        if not self.is_blocking:
            # 记录原始血量用于计算损失
            original_health = self.health
            
            # 应用伤害
            self.health -= damage
            self.state = CharacterState.HIT
            # 重置动画帧，避免显示多个小人
            self.animation_frame = 0
            self.animation_timer = 0
            # 重置受击恢复计时器
            self.hit_recovery_timer = 0
            
            # 添加击退效果 - 增强击退效果
            knockback_force = 10.0 if damage >= 3 else 5.0  # 增加击退力
            # 根据攻击方向决定击退方向
            if self.direction == Direction.RIGHT:
                self.vel_x = -knockback_force  # 向左击退
            else:
                self.vel_x = knockback_force   # 向右击退
            
            # 检查是否被击败
            if self.health <= 0:
                self.health = 0
                self.state = CharacterState.DEFEATED
                self.animation_frame = 0
                self.animation_timer = 0
            
            # 播放受击音效
            if self.hit_sound:
                self.hit_sound.play()
            
            # 返回实际损失的血量（用于显示伤害数值）
            return original_health - self.health
        return 0  # 如果格挡成功，返回0表示没有受到伤害
    
    def get_state_data(self):
        """获取角色状态数据（用于AI）"""
        return {
            'x': self.x,
            'y': self.y,
            'vel_x': self.vel_x,
            'vel_y': self.vel_y,
            'is_jumping': self.is_jumping,
            'is_crouching': self.is_crouching,
            'is_blocking': self.is_blocking,
            'is_attacking': self.is_attacking,
            'health': self.health,
            'state': self.state.value,
            'direction': self.direction.value
        }
    
    def render_health_bar(self, screen, x, y, width, height, is_player_one):
        """渲染血条"""
        # 背景
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        
        # 血量百分比
        health_percent = self.health / MAX_HEALTH
        health_width = int(width * health_percent)
        
        # 血条颜色随血量变化
        if health_percent > 0.6:
            color = (0, 255, 0)  # 绿色
        elif health_percent > 0.3:
            color = (255, 255, 0)  # 黄色
        else:
            color = (255, 0, 0)  # 红色
        
        # 根据是否为玩家一来决定血条绘制方向
        if is_player_one:
            pygame.draw.rect(screen, color, (x, y, health_width, height))
        else:
            pygame.draw.rect(screen, color, (x + width - health_width, y, health_width, height))
        
        # 边框
        pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height), 2)
    
    def _handle_character_collision(self, opponent):
        """处理与对手的碰撞
        
        Args:
            opponent: 对手角色
        """
        # 只在两个角色都在地面上，且都不在攻击状态时处理碰撞
        if (self.is_on_ground() and opponent.is_on_ground() and 
            not self.is_attacking and not opponent.is_attacking and
            self.state != CharacterState.HIT and opponent.state != CharacterState.HIT and
            self.state != CharacterState.DEFEATED and opponent.state != CharacterState.DEFEATED):
            
            # 计算角色之间的距离
            distance = abs(self.x - opponent.x)
            min_distance = self.width * 1.0  # 增加最小距离为角色宽度的100%（原为80%）
            
            # 如果距离太小，进行推开处理
            if distance < min_distance:
                # 计算推力方向和大小
                push_direction = 1 if self.x < opponent.x else -1
                push_amount = (min_distance - distance) * 0.7  # 增加推力强度（原为/2）
                
                # 应用推力，将两个角色推开
                self.x -= push_direction * push_amount
                opponent.x += push_direction * push_amount
                
                # 确保不会推出屏幕边界
                if self.x < 0:
                    self.x = 0
                elif self.x > 800 - self.width:
                    self.x = 800 - self.width
                
                if opponent.x < 0:
                    opponent.x = 0
                elif opponent.x > 800 - opponent.width:
                    opponent.x = 800 - opponent.width 