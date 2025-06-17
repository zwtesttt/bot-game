#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
from src.characters.character import Character, CharacterState, Direction

class Ryu(Character):
    """Ryu角色类"""
    
    def __init__(self, x, y):
        """初始化Ryu角色"""
        super().__init__(x, y, "Ryu")
        # 角色特性 - Ryu以平衡的战斗风格著称
        self.special_attributes = {
            "speed": 1.0,      # 速度倍率
            "strength": 1.2,   # 力量倍率 - Ryu拳脚稍重
            "defense": 1.0,    # 防御倍率
            "jump_height": 1.0 # 跳跃高度倍率
        }
        
        # 加载Ryu特有的音效
        self._load_character_sounds()
    
    def _load_character_sounds(self):
        """加载角色特有的音效"""
        sounds_dir = os.path.join("assets", "sounds", "ryu")
        if os.path.exists(sounds_dir):
            try:
                # 跳跃音效
                jump_sound_path = os.path.join(sounds_dir, "jump.wav")
                if os.path.exists(jump_sound_path):
                    self.jump_sound = pygame.mixer.Sound(jump_sound_path)
                    self.jump_sound.set_volume(0.4)
                
                # 攻击音效
                punch_sound_path = os.path.join(sounds_dir, "punch.wav")
                if os.path.exists(punch_sound_path):
                    self.punch_sound = pygame.mixer.Sound(punch_sound_path)
                    self.punch_sound.set_volume(0.5)
                
                # 踢腿音效
                kick_sound_path = os.path.join(sounds_dir, "kick.wav")
                if os.path.exists(kick_sound_path):
                    self.kick_sound = pygame.mixer.Sound(kick_sound_path)
                    self.kick_sound.set_volume(0.5)
                
                # 受击音效
                hit_sound_path = os.path.join(sounds_dir, "hit.wav")
                if os.path.exists(hit_sound_path):
                    self.hit_sound = pygame.mixer.Sound(hit_sound_path)
                    self.hit_sound.set_volume(0.6)
            except Exception as e:
                print(f"加载Ryu音效失败: {e}")
    
    def _load_sprites(self):
        """加载Ryu的精灵图"""
        sprites = {}
        
        # 检查是否存在实际的图像资源
        base_path = os.path.join("assets", "images", "characters", "ryu")
        has_sprite_images = os.path.exists(base_path)
        
        # 为每个状态和方向创建图像
        for state in CharacterState:
            sprites[state] = {Direction.RIGHT: [], Direction.LEFT: []}
            
            # 每个状态的帧数和缩放系数
            frames_config = {
                CharacterState.IDLE: {"frames": 4, "scale": 1.0},
                CharacterState.WALKING: {"frames": 4, "scale": 1.0},
                CharacterState.RUNNING: {"frames": 4, "scale": 1.1},
                CharacterState.JUMPING: {"frames": 3, "scale": 1.0},
                CharacterState.FALLING: {"frames": 3, "scale": 1.0},
                CharacterState.CROUCHING: {"frames": 1, "scale": 0.9},
                CharacterState.LIGHT_PUNCH: {"frames": 3, "scale": 1.1},
                CharacterState.HEAVY_PUNCH: {"frames": 3, "scale": 1.2},
                CharacterState.LIGHT_KICK: {"frames": 3, "scale": 1.1},
                CharacterState.HEAVY_KICK: {"frames": 3, "scale": 1.2},
                CharacterState.BLOCKING: {"frames": 1, "scale": 0.9},
                CharacterState.HIT: {"frames": 2, "scale": 1.0},
                CharacterState.DEFEATED: {"frames": 1, "scale": 0.8}
            }
            
            frames = frames_config[state]["frames"]
            scale_multiplier = frames_config[state]["scale"]
            
            # 使用实际的精灵图（如果存在）
            if has_sprite_images:
                try:
                    # 根据状态选择不同的精灵表
                    sprite_sheet_path = None
                    if state == CharacterState.IDLE:
                        sprite_sheet_path = os.path.join(base_path, "idle.png")
                    elif state == CharacterState.WALKING:
                        # 尝试使用专用的行走精灵图，如果没有则使用idle
                        walk_path = os.path.join(base_path, "walk.png")
                        sprite_sheet_path = walk_path if os.path.exists(walk_path) else os.path.join(base_path, "idle.png")
                    elif state == CharacterState.RUNNING:
                        # 尝试使用专用的奔跑精灵图，如果没有则使用walk或idle
                        run_path = os.path.join(base_path, "run.png")
                        walk_path = os.path.join(base_path, "walk.png")
                        if os.path.exists(run_path):
                            sprite_sheet_path = run_path
                        elif os.path.exists(walk_path):
                            sprite_sheet_path = walk_path
                        else:
                            sprite_sheet_path = os.path.join(base_path, "idle.png")
                    elif state == CharacterState.JUMPING or state == CharacterState.FALLING:
                        # 使用专用的跳跃精灵图
                        sprite_sheet_path = os.path.join(base_path, "jump.png")
                    elif state in [CharacterState.LIGHT_PUNCH, CharacterState.HEAVY_PUNCH]:
                        # 尝试使用不同的拳击精灵图
                        if state == CharacterState.LIGHT_PUNCH:
                            light_punch_path = os.path.join(base_path, "light_punch.png")
                            sprite_sheet_path = light_punch_path if os.path.exists(light_punch_path) else os.path.join(base_path, "punch.png")
                        else:
                            heavy_punch_path = os.path.join(base_path, "heavy_punch.png")
                            sprite_sheet_path = heavy_punch_path if os.path.exists(heavy_punch_path) else os.path.join(base_path, "punch.png")
                    elif state in [CharacterState.LIGHT_KICK, CharacterState.HEAVY_KICK]:
                        # 尝试使用不同的踢腿精灵图
                        if state == CharacterState.LIGHT_KICK:
                            light_kick_path = os.path.join(base_path, "light_kick.png")
                            sprite_sheet_path = light_kick_path if os.path.exists(light_kick_path) else os.path.join(base_path, "kick.png")
                        else:
                            heavy_kick_path = os.path.join(base_path, "heavy_kick.png")
                            sprite_sheet_path = heavy_kick_path if os.path.exists(heavy_kick_path) else os.path.join(base_path, "kick.png")
                    elif state == CharacterState.CROUCHING:
                        # 使用专用的蹲下精灵图
                        crouch_path = os.path.join(base_path, "crouch.png")
                        sprite_sheet_path = crouch_path if os.path.exists(crouch_path) else os.path.join(base_path, "idle.png")
                    elif state == CharacterState.BLOCKING:
                        # 使用专用的格挡精灵图
                        block_path = os.path.join(base_path, "block.png")
                        sprite_sheet_path = block_path if os.path.exists(block_path) else os.path.join(base_path, "idle.png")
                    elif state == CharacterState.HIT:
                        # 使用专用的受击精灵图
                        sprite_sheet_path = os.path.join(base_path, "hit.png")
                    elif state == CharacterState.DEFEATED:
                        # 使用专用的被击败精灵图
                        defeated_path = os.path.join(base_path, "defeated.png")
                        sprite_sheet_path = defeated_path if os.path.exists(defeated_path) else os.path.join(base_path, "hit.png")
                    
                    # 如果有对应的精灵表，加载它
                    if sprite_sheet_path and os.path.exists(sprite_sheet_path):
                        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
                        # 精灵表尺寸
                        sprite_width = sprite_sheet.get_width() // frames
                        sprite_height = sprite_sheet.get_height()
                        
                        # 从精灵表中提取每一帧
                        for i in range(frames):
                            # 创建一个新的Surface并将精灵的一部分绘制到其上
                            frame = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                            frame.blit(sprite_sheet, (0, 0), (i * sprite_width, 0, sprite_width, sprite_height))
                            
                            # 确保尺寸正确 - 根据状态应用不同的缩放
                            base_scale = min(self.width / sprite_width, self.height / sprite_height)
                            adjusted_scale = base_scale * scale_multiplier
                            new_width = int(sprite_width * adjusted_scale)
                            new_height = int(sprite_height * adjusted_scale)
                            
                            # 缩放图像
                            frame = pygame.transform.scale(frame, (new_width, new_height))
                            
                            # 创建一个空白图像，尺寸为角色尺寸
                            final_frame = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                            
                            # 根据状态调整放置位置
                            x_offset = (self.width - new_width) // 2
                            
                            # 对于不同状态使用不同的y偏移
                            if state == CharacterState.CROUCHING:
                                y_offset = self.height - new_height + 10  # 蹲下时位置更低
                            elif state in [CharacterState.JUMPING, CharacterState.FALLING]:
                                y_offset = self.height - new_height - 10  # 跳跃时位置更高
                            elif state in [CharacterState.LIGHT_KICK, CharacterState.HEAVY_KICK]:
                                y_offset = self.height - new_height - 5  # 踢腿时略微升高
                            else:
                                y_offset = self.height - new_height
                            
                            final_frame.blit(frame, (x_offset, y_offset))
                            
                            # 添加到右方向
                            sprites[state][Direction.RIGHT].append(final_frame)
                            
                            # 翻转作为左方向
                            flipped = pygame.transform.flip(final_frame, True, False)
                            sprites[state][Direction.LEFT].append(flipped)
                        
                        # 如果成功加载了精灵，跳过下面的默认矩形生成
                        continue
                except Exception as e:
                    print(f"加载Ryu精灵图失败: {e}")
            
            # 如果没有实际图像或加载失败，生成默认矩形
            # 生成每个状态的颜色
            color = (255, 255, 255)  # 默认白色
            if state == CharacterState.IDLE:
                color = (0, 0, 255)  # 蓝色
            elif state == CharacterState.WALKING:
                color = (0, 255, 0)  # 绿色
            elif state == CharacterState.JUMPING:
                color = (255, 255, 0)  # 黄色
            elif state == CharacterState.FALLING:
                color = (255, 165, 0)  # 橙色
            elif state == CharacterState.CROUCHING:
                color = (128, 0, 128)  # 紫色
            elif state == CharacterState.LIGHT_PUNCH:
                color = (255, 0, 0)  # 红色
            elif state == CharacterState.HEAVY_PUNCH:
                color = (220, 20, 60)  # 深红色
            elif state == CharacterState.LIGHT_KICK:
                color = (0, 255, 255)  # 青色
            elif state == CharacterState.HEAVY_KICK:
                color = (0, 128, 255)  # 深青色
            elif state == CharacterState.BLOCKING:
                color = (128, 128, 128)  # 灰色
            elif state == CharacterState.HIT:
                color = (255, 0, 255)  # 粉色
            elif state == CharacterState.DEFEATED:
                color = (0, 0, 0)  # 黑色
            
            # 创建帧
            for i in range(frames):
                # 创建临时画面
                temp_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(temp_surf, color, (0, 0, self.width, self.height))
                
                # 添加帧号文本
                font = pygame.font.SysFont(None, 24)
                text = font.render(f"{state.name} {i+1}", True, (255, 255, 255))
                temp_surf.blit(text, (10, 10))
                
                # 添加到两个方向
                sprites[state][Direction.RIGHT].append(temp_surf)
                
                # 翻转作为左方向
                flipped = pygame.transform.flip(temp_surf, True, False)
                sprites[state][Direction.LEFT].append(flipped)
        
        return sprites
    
    # 重写特定方法给予Ryu独特的能力
    def light_punch(self):
        """Ryu的轻拳（伤害稍高）"""
        super().light_punch()
        # 如果需要可以修改特定属性，例如伤害调整
    
    def heavy_punch(self):
        """Ryu的重拳（伤害更高）"""
        super().heavy_punch()
        # 增加攻击判定框大小，使攻击更加明显
        if self.attack_hitbox:
            # 扩大攻击判定框
            if self.direction == Direction.RIGHT:
                self.attack_hitbox.width += 10
            else:
                self.attack_hitbox.x -= 10
                self.attack_hitbox.width += 10 