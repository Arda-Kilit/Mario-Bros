"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║  SUPER MARIO BROS - ULTIMATE PROFESSIONAL EDITION v3.2.2                       ║
║  MUSH_S HATASI DÜZELTİLDİ - TÜM HATALAR GİDERİLDİ                            ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

import pygame, random, math, time, json, sys, cv2, numpy as np, threading
if sys.platform.startswith('win'):
    if sys.stdout is not None:
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    if sys.stderr is not None:
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass
import mediapipe as mp
import mediapipe.python.solutions.hands as mp_hands
from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum, auto

# ═══════════════════════════════════════════════════════════════════════════════════
# GELİŞMİŞ SES SİSTEMİ
# ═══════════════════════════════════════════════════════════════════════════════════

class SoundGenerator:
    """Programatik ses üretici - Gelişmiş NES tarzı sesler (Önbellekli sürüm)"""
    _sounds = {}
    
    @staticmethod
    def _make_stereo(data):
        if len(data.shape) == 1:
            return np.column_stack((data, data.copy()))
        return data
    
    @staticmethod
    def fade_out(buf, fade_duration=0.02, sample_rate=44100):
        fade_samples = int(sample_rate * fade_duration)
        if fade_samples >= len(buf):
            fade_samples = len(buf) // 2
        
        if fade_samples > 0:
            fade = np.linspace(1, 0, fade_samples)
            if len(buf.shape) == 2:
                buf[-fade_samples:] = (buf[-fade_samples:] * fade[:, np.newaxis]).astype(np.int16)
            else:
                buf[-fade_samples:] = (buf[-fade_samples:] * fade).astype(np.int16)
        return buf

    @classmethod
    def pre_generate_all(cls):
        rate = 44100
        
        # 1. Jump
        dur = 0.12
        t = np.arange(int(rate * dur)) / rate
        freq = 400 + 600 * (t / dur)
        data = (0.3 * 32767 * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        cls._sounds['jump'] = cls._create_sound(data)
        
        # 2. Double Jump
        dur = 0.1
        t = np.arange(int(rate * dur)) / rate
        freq = 600 + 800 * (t / dur)
        data = (0.35 * 32767 * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        cls._sounds['double_jump'] = cls._create_sound(data)
        
        # 3. Coin
        dur = 0.15
        t = np.arange(int(rate * dur)) / rate
        freq = np.where(t < 0.07, 988, 1319)
        data = (0.25 * 32767 * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        cls._sounds['coin'] = cls._create_sound(data)
        
        # 4. Stomp
        dur = 0.12
        t = np.arange(int(rate * dur)) / rate
        freq = 200 - 150 * (t / dur)
        data = (0.3 * 32767 * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        cls._sounds['stomp'] = cls._create_sound(data)
        
        # 5. Powerup
        dur = 0.6
        t = np.arange(int(rate * dur)) / rate
        notes = np.array([523, 659, 784, 1047])
        note_idx = np.minimum((t / (dur/4)).astype(int), 3)
        freq = notes[note_idx]
        data = (0.25 * 32767 * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        cls._sounds['powerup'] = cls._create_sound(data)
        
        # 6. Star
        dur = 0.4
        t = np.arange(int(rate * dur)) / rate
        freq = 880 + 440 * np.sin(2 * np.pi * 12 * t)
        data = (0.2 * 32767 * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        cls._sounds['star'] = cls._create_sound(data)
        
        # 7. Bump
        dur = 0.06
        samples = int(rate * dur)
        data = (0.15 * 32767 * (np.random.random(samples) * 2 - 1) * 
                np.linspace(1, 0, samples)).astype(np.int16)
        cls._sounds['bump'] = cls._create_sound(data)
        
        # 8. Death
        dur = 0.8
        t = np.arange(int(rate * dur)) / rate
        notes = np.array([659, 587, 523, 440, 330])
        note_idx = np.minimum((t / (dur/5)).astype(int), 4)
        freq = notes[note_idx]
        data = (0.3 * 32767 * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        cls._sounds['death'] = cls._create_sound(data)
        
        # 9. Gameover
        dur = 1.5
        t = np.arange(int(rate * dur)) / rate
        notes = np.array([392, 330, 262, 196])
        note_idx = np.minimum((t / (dur/4)).astype(int), 3)
        freq = notes[note_idx]
        envelope = 1 - t/dur
        data = (0.3 * 32767 * envelope * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        cls._sounds['gameover'] = cls._create_sound(data)
        
        # 10. Hover
        dur = 0.05
        t = np.arange(int(rate * dur)) / rate
        freq = 800 + 400 * (t / dur)
        data = (0.12 * 32767 * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        cls._sounds['hover'] = cls._create_sound(data)
        
        # 11. Click
        dur = 0.12
        t = np.arange(int(rate * dur)) / rate
        freq = np.where(t < 0.05, 1000, 1500)
        data = (0.18 * 32767 * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        cls._sounds['click'] = cls._create_sound(data)

    @classmethod
    def _create_sound(cls, data, rate=44100):
        try:
            if len(data.shape) == 1:
                data = np.column_stack((data, data.copy()))
            data = cls.fade_out(data, 0.02, rate)
            data = np.ascontiguousarray(data.astype(np.int16))
            return pygame.sndarray.make_sound(data)
        except:
            return None

    @classmethod
    def play_sound_cached(cls, name, volume=0.5):
        try:
            sound = cls._sounds.get(name)
            if sound is not None:
                sound.set_volume(min(1.0, max(0.0, volume)))
                sound.play()
                return sound
        except:
            pass
        return None

    @classmethod
    def jump_sound(cls, volume=0.4): return cls.play_sound_cached('jump', volume)
    @classmethod
    def double_jump_sound(cls, volume=0.4): return cls.play_sound_cached('double_jump', volume)
    @classmethod
    def coin_sound(cls, volume=0.5): return cls.play_sound_cached('coin', volume)
    @classmethod
    def stomp_sound(cls, volume=0.5): return cls.play_sound_cached('stomp', volume)
    @classmethod
    def powerup_sound(cls, volume=0.5): return cls.play_sound_cached('powerup', volume)
    @classmethod
    def star_sound(cls, volume=0.4): return cls.play_sound_cached('star', volume)
    @classmethod
    def bump_sound(cls, volume=0.3): return cls.play_sound_cached('bump', volume)
    @classmethod
    def death_sound(cls, volume=0.5): return cls.play_sound_cached('death', volume)
    @classmethod
    def gameover_sound(cls, volume=0.5): return cls.play_sound_cached('gameover', volume)
    @classmethod
    def hover_sound(cls, volume=0.25): return cls.play_sound_cached('hover', volume)
    @classmethod
    def click_sound(cls, volume=0.45): return cls.play_sound_cached('click', volume)
    @classmethod
    def combo_sound(cls, combo_level, volume=0.4): return cls.play_sound_cached('double_jump', volume)
    @classmethod
    def checkpoint_sound(cls, volume=0.5): return cls.play_sound_cached('powerup', volume)


# ═══════════════════════════════════════════════════════════════════════════════════
# YAPILANDIRMA
# ═══════════════════════════════════════════════════════════════════════════════════

SW, SH = 1280, 720
TILE = 32
GY = int(SH * 0.88)
WW = 18000
GRAV = 0.85
JUMP = -16.5
HIGH_JUMP = -19.0
MAX_SPD = 11.0
MAX_RUN_SPD = 15.0
ACC = 1.0
RUN_ACC = 1.4
FRICTION = 0.85
AIR_FRICTION = 0.95
FPS = 60
LVL_TIME = 400
LIVES = 3
STAR_T = 600
INV_T = 180
COIN_S = 200
STOMP_S = 100
MUSH_SCORE = 1000  # DÜZELTİLDİ: MUSH_S yerine MUSH_SCORE kullan
COMBO_MULTIPLIER = 50
CAM_W, CAM_H = 640, 480
HAND_CONF = 0.3
GESTURE_CD = 0.04
HAND_SENSITIVITY = 2.0
SCORE_F = "mario_ultimate_score.json"

SHADOW_ALPHA = 80
TRAIL_LENGTH = 5
VIGNETTE_STRENGTH = 0.2

# ═══════════════════════════════════════════════════════════════════════════════════
# RENK PALETİ
# ═══════════════════════════════════════════════════════════════════════════════════

SKY = (92, 148, 252)
SKY_TOP = (40, 100, 240)
SKY_BOTTOM = (140, 180, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (252, 0, 0)
GREEN = (0, 255, 0)
GOLD = (252, 216, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
MRED = (220, 0, 0)
MSKIN = (252, 180, 128)
MBLUE = (0, 0, 220)
MBROWN = (136, 72, 0)
GMBODY = (176, 88, 48)
GMHEAD = (200, 112, 64)
KGREEN = (0, 184, 0)
KHEAD = (252, 208, 96)
BRICK = (200, 76, 12)
BRICK_D = (168, 56, 8)
GRASS = (0, 168, 0)
GRASS_L = (56, 208, 56)
GROUND = (184, 104, 32)
GROUND_D = (152, 88, 24)
QBLOCK = (248, 208, 0)
QBLOCK_D = (216, 168, 0)
PIPE_GREEN = (0, 184, 0)
PIPE_L = (56, 216, 56)
PIPE_D = (0, 136, 0)
MUSH_RED = (252, 0, 0)      # DÜZELTİLDİ: MUSH_R yerine MUSH_RED
MUSH_WHITE = (255, 255, 255) # DÜZELTİLDİ: MUSH_W yerine MUSH_WHITE
MUSH_STEM = (248, 240, 208)  # DÜZELTİLDİ: MUSH_S yerine MUSH_STEM (renk)
BUTTON_BG = (0, 80, 200)
BUTTON_HOVER = (0, 120, 255)
MENU_BG = (0, 0, 40)
SETTINGS_BG = (20, 20, 60)

MOUNTAIN_FAR = (120, 130, 180)
MOUNTAIN_NEAR = (168, 128, 96)
HILL_FAR = (100, 180, 100)
HILL_NEAR = (0, 200, 0)
CLOUD_COLOR = (255, 255, 255)
CLOUD_SHADOW = (230, 230, 245)

FIRE_ORANGE = (255, 150, 0)
SHIELD_BLUE = (100, 150, 255)

# ═══════════════════════════════════════════════════════════════════════════════════
# ENUM
# ═══════════════════════════════════════════════════════════════════════════════════

class State(Enum): 
    MENU=0; PLAY=1; PAUSE=2; OVER=3; CONTROLS=4; TRANSITION=5; WIN=6; SETTINGS=7

class BType(Enum): 
    GROUND=0; GRASS=1; BRICK=2; QUESTION=3; PIPE=4; CASTLE=5; FLAG=6; 
    HIDDEN=7; CHECKPOINT=8

class EType(Enum): 
    GOOMBA=0; KOOPA=1; PIRANHA=2

class Dir(Enum): 
    LEFT=-1; RIGHT=1

class PowerUp(Enum): 
    NONE=0; MUSHROOM=1; FIRE=2; STAR=3; SHIELD=4; SPEED=5

class Weather(Enum):
    CLEAR=0; RAIN=1; SNOW=2; NIGHT=3

class Difficulty(Enum):
    EASY=0; NORMAL=1; HARD=2

# ═══════════════════════════════════════════════════════════════════════════════════
# PARTİKÜL VE EFEKT SİSTEMİ
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class Particle:
    x: float; y: float
    vx: float; vy: float
    life: float = 1.0
    max_life: float = 1.0
    size: int = 3
    start_size: int = 3
    end_size: int = 1
    color: Tuple = (255, 255, 255)
    end_color: Optional[Tuple] = None
    gravity: float = 0.2
    shape: str = "circle"
    angle: float = 0.0
    angular_velocity: float = 0.0
    bounces: int = 0
    
    @property
    def alive(self): return self.life > 0
    
    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += self.gravity * dt * 60
        self.angle += self.angular_velocity * dt * 60
        
        # Bouncing on ground!
        if self.bounces > 0 and self.y >= GY - self.size:
            self.y = GY - self.size
            self.vy = -self.vy * 0.5
            self.vx *= 0.8
            self.bounces -= 1
            
        self.life -= dt
        progress = 1 - (self.life / self.max_life)
        self.size = int(self.start_size + (self.end_size - self.start_size) * progress)
    
    def get_color(self):
        progress = 1 - (self.life / self.max_life)
        alpha = max(0, min(255, int(255 * self.life / self.max_life)))
        
        if self.end_color is not None and len(self.end_color) >= 3:
            r = int(self.color[0] + (self.end_color[0] - self.color[0]) * progress)
            g = int(self.color[1] + (self.end_color[1] - self.color[1]) * progress)
            b = int(self.color[2] + (self.end_color[2] - self.color[2]) * progress)
            return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), alpha)
        else:
            return (self.color[0], self.color[1], self.color[2], alpha)

@dataclass
class ScorePopup:
    x: float; y: float
    text: str
    color: Tuple = (255, 255, 255)
    life: float = 1.0
    max_life: float = 1.0
    vy: float = -3.0
    scale: float = 1.0
    pulse: bool = False
    
    @property
    def alive(self): return self.life > 0
    
    def update(self, dt):
        self.y += self.vy * dt * 60
        self.vy *= 0.98
        self.life -= dt
        if self.pulse:
            self.scale = 1 + math.sin(time.time() * 10) * 0.1

@dataclass
class ScreenEffect:
    type: str = "flash"
    intensity: float = 1.0
    duration: float = 0.5
    timer: float = 0.5
    color: Tuple = (255, 255, 255)
    
    @property
    def alive(self): return self.timer > 0
    
    def update(self, dt):
        self.timer -= dt
    
    def get_alpha(self):
        return max(0, min(255, int(255 * self.timer / self.duration)))

# ═══════════════════════════════════════════════════════════════════════════════════
# VERİ SINIFLARI
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class Player:
    x: float; y: float
    w: int=32; h: int=48
    vx: float=0; vy: float=0
    ground: bool=False
    jumps: int=2
    max_jumps: int=2
    dir: Dir=Dir.RIGHT
    anim: float=0
    inv: int=0
    big: bool=False
    star: bool=False
    star_t: int=0
    shield: bool=False
    shield_t: int=0
    speed_boost: bool=False
    speed_t: int=0
    lives: int=LIVES
    power: PowerUp=PowerUp.NONE
    combo: int=0
    combo_timer: float=0
    max_combo: int=0
    trail: deque = field(default_factory=lambda: deque(maxlen=TRAIL_LENGTH))
    ducking: bool = False
    ground_pound: bool = False
    wall_sliding: bool = False
    dash_charge: float = 0
    perfect_jump_timer: float = 0
    was_on_ground: bool = True
    
    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.w, self.h)
    
    @property
    def speed(self): return abs(self.vx)

@dataclass
class Block:
    x: float; y: float
    w: int=32; h: int=32
    type: BType=BType.GROUND
    used: bool=False
    item: str=""
    bounce: float=0
    bounce_t: float=0
    hidden: bool=False
    
    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

@dataclass
class Enemy:
    x: float; y: float
    w: int=32; h: int=32
    type: EType=EType.GOOMBA
    vx: float=1.5
    alive: bool=True
    anim: float=0
    dead: bool=False
    dead_t: float=0
    vy: float=0.0
    
    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

@dataclass
class Coin:
    x: float; y: float
    taken: bool=False
    off: float=0
    magnet_timer: float=0
    
    @property
    def rect(self): return pygame.Rect(int(self.x-8), int(self.y-8), 16, 16)

@dataclass
class Mushroom:
    x: float; y: float
    taken: bool=False
    vx: float=2
    vy: float=0.0
    anim: float=0
    spawn: bool=True
    spawn_t: float=0.5
    type: str="super"
    
    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), 32, 32)

@dataclass
class Fireball:
    x: float; y: float
    vx: float=6; vy: float=-2
    life: float=2.0
    bounces: int=3
    reflected: bool = False
    
    @property
    def rect(self): return pygame.Rect(int(self.x-8), int(self.y-8), 16, 16)
    @property
    def alive(self): return self.life > 0

@dataclass
class BowserBot:
    x: float; y: float
    w: int = 96
    h: int = 96
    vx: float = 2.0
    vy: float = 0.0
    health: int = 15
    max_health: int = 15
    state: str = "descending"  # "descending", "active", "jumping", "dead"
    timer: float = 0.0
    phase: int = 1
    shielded: bool = False
    shield_t: float = 0.0
    inv_t: float = 0.0
    anim: float = 0.0
    
    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

@dataclass
class Checkpoint:
    x: float; y: float
    activated: bool=False
    anim: float=0

@dataclass
class SettingsButton:
    x: int; y: int; w: int; h: int
    text: str; key: str
    value: any
    min_val: any = None
    max_val: any = None
    step: any = None
    options: List = None
    
    def draw(self, screen, font, selected=False):
        color = GOLD if selected else WHITE
        border_color = GOLD if selected else GRAY
        
        pygame.draw.rect(screen, (30, 30, 60), (self.x-5, self.y-5, self.w+10, self.h+10), border_radius=8)
        pygame.draw.rect(screen, border_color, (self.x-5, self.y-5, self.w+10, self.h+10), 2, border_radius=8)
        
        display_text = self.text
        if self.options:
            display_text = f"{self.text}: {self.options[self.value]}"
        elif self.min_val is not None:
            display_text = f"{self.text}: {self.value}"
        
        txt = font.render(display_text, True, color)
        screen.blit(txt, (self.x + 10, self.y + self.h//2 - txt.get_height()//2))
        
        if self.options or self.min_val is not None:
            left_arrow = font.render("<", True, GRAY)
            right_arrow = font.render(">", True, GRAY)
            screen.blit(left_arrow, (self.x + self.w - 60, self.y + self.h//2 - left_arrow.get_height()//2))
            screen.blit(right_arrow, (self.x + self.w - 30, self.y + self.h//2 - right_arrow.get_height()//2))
    
    def is_clicked_left(self, pos):
        clicked = (self.x + self.w - 70 <= pos[0] <= self.x + self.w - 40 and 
                self.y <= pos[1] <= self.y + self.h)
        if clicked:
            SoundGenerator.click_sound()
        return clicked
    
    def is_clicked_right(self, pos):
        clicked = (self.x + self.w - 40 <= pos[0] <= self.x + self.w - 10 and 
                self.y <= pos[1] <= self.y + self.h)
        if clicked:
            SoundGenerator.click_sound()
        return clicked
    
    def change_value(self, direction):
        if self.options:
            self.value = (self.value + direction) % len(self.options)
        elif self.min_val is not None:
            self.value = max(self.min_val, min(self.max_val, self.value + direction * self.step))

# ═══════════════════════════════════════════════════════════════════════════════════
# BUTON SINIFI
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class Button:
    x: int; y: int; w: int; h: int
    text: str; action: str
    color: Tuple = BUTTON_BG
    hover_color: Tuple = BUTTON_HOVER
    text_color: Tuple = WHITE
    font_size: int = 48
    pulse: float = 0
    icon: str = ""
    hovered: bool = False
    
    def draw(self, screen, mouse_pos, font):
        hover = self.x <= mouse_pos[0] <= self.x+self.w and self.y <= mouse_pos[1] <= self.y+self.h
        c = self.hover_color if hover else self.color
        
        if hover and not getattr(self, 'hovered', False):
            SoundGenerator.hover_sound()
            self.hovered = True
        elif not hover:
            self.hovered = False
            
        if hover:
            self.pulse = (self.pulse + 0.05) % (2 * math.pi)
            scale = 1 + math.sin(self.pulse) * 0.03
            rw, rh = int(self.w * scale), int(self.h * scale)
            rx, ry = self.x - (rw - self.w)//2, self.y - (rh - self.h)//2
        else:
            self.pulse = 0
            rw, rh, rx, ry = self.w, self.h, self.x, self.y
        
        shadow_surf = pygame.Surface((rw + 8, rh + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 120), (8, 8, rw, rh), border_radius=15)
        screen.blit(shadow_surf, (rx-4, ry-4))
        
        for i in range(rh):
            ratio = i / rh
            r = int(c[0] + (255 - c[0]) * ratio * 0.2)
            g = int(c[1] + (255 - c[1]) * ratio * 0.2)
            b = int(c[2] + (255 - c[2]) * ratio * 0.2)
            pygame.draw.line(screen, (r, g, b), (rx, ry+i), (rx+rw, ry+i))
        
        pygame.draw.rect(screen, c, (rx, ry, rw, rh), border_radius=15)
        
        highlight = pygame.Surface((rw, rh//2), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 60))
        screen.blit(highlight, (rx, ry), special_flags=pygame.BLEND_RGBA_ADD)
        
        border_color = WHITE if hover else (200, 200, 200)
        pygame.draw.rect(screen, border_color, (rx, ry, rw, rh), 3, border_radius=15)
        
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        txt = font.render(display_text, True, self.text_color)
        txt_rect = txt.get_rect(center=(rx+rw//2, ry+rh//2))
        
        shadow_txt = font.render(display_text, True, (0, 0, 0))
        screen.blit(shadow_txt, (txt_rect.x+2, txt_rect.y+2))
        screen.blit(txt, txt_rect)
        
        return hover
    
    def is_clicked(self, mouse_pos, mouse_click):
        hover = self.x <= mouse_pos[0] <= self.x+self.w and self.y <= mouse_pos[1] <= self.y+self.h
        if hover and mouse_click:
            SoundGenerator.click_sound()
            return True
        return False

# ═══════════════════════════════════════════════════════════════════════════════════

# Caching systems for drawing performance
_goomba_cache = {}
_koopa_cache = {}
_piranha_cache = {}
_coin_cache = {}
_brick_cache = {}
_qblock_cache = {}
_pipe_cache = {}
_mushroom_cache = {}
_shadow_cache = {}
_pixel_heart_cache = {}
_pixel_clock_cache = {}
_pixel_star_cache = {}
_menu_mushroom_cache = {}
_mario_cache = {}

def draw_retro_text(s, text, font, x, y, color=(255, 255, 255), shadow_color=(0, 0, 0)):
    shadow = font.render(str(text), True, shadow_color)
    s.blit(shadow, (x + 2, y + 2))
    lbl = font.render(str(text), True, color)
    s.blit(lbl, (x, y))

def draw_menu_mushroom(s, x, y, size=24):
    key = size
    if key not in _menu_mushroom_cache:
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        grid = [
            "......RRRR......",
            "....RRRRRRRR....",
            "...RRWWRRRRWWR..",
            "..RRWWRRRRRRWWR.",
            ".RRRRRRWWRRRRRRR",
            ".RRRRRRWWRRRRRRR",
            "RRRWRRRRRRRRWRRR",
            "RRRWRRRRRRRRWRRR",
            "RRRRRRRRRRRRRRRR",
            "RRRRRRRRRRRRRRRR",
            "....SSSSSSSS....",
            "...SSKSKSSKSS...",
            "...SSKSKSSKSS...",
            "...SSSSSSSSSS...",
            "....SSSSSSSS....",
            ".....SSSSSS....."
        ]
        colors = {
            '.': (0,0,0,0),
            'R': (220, 20, 20),
            'W': (255, 255, 255),
            'S': (255, 220, 180),
            'K': (0, 0, 0)
        }
        for py, row in enumerate(grid):
            for px, char in enumerate(row):
                surf.set_at((px, py), colors[char])
        _menu_mushroom_cache[key] = pygame.transform.scale(surf, (size, size))
    if s is not None:
        s.blit(_menu_mushroom_cache[key], (x, y))

def draw_pixel_heart(s, x, y, scale=3):
    key = scale
    if key not in _pixel_heart_cache:
        grid = [
            ".XX.XX.",
            "XXXXXXX",
            "XXXXXXX",
            "XXXXXXX",
            ".XXXXX.",
            "..XXX..",
            "...X..."
        ]
        surf = pygame.Surface((7, 7), pygame.SRCALPHA)
        for py, row in enumerate(grid):
            for px, char in enumerate(row):
                if char == 'X':
                    surf.set_at((px, py), (255, 50, 50))
        _pixel_heart_cache[key] = pygame.transform.scale(surf, (7 * scale, 7 * scale))
    if s is not None:
        s.blit(_pixel_heart_cache[key], (x, y))

def draw_pixel_clock(s, x, y, scale=3):
    key = scale
    if key not in _pixel_clock_cache:
        grid = [
            "..XXX..",
            ".X...X.",
            "X..X..X",
            "X..XX.X",
            "X.....X",
            ".X...X.",
            "..XXX.."
        ]
        surf = pygame.Surface((7, 7), pygame.SRCALPHA)
        for py, row in enumerate(grid):
            for px, char in enumerate(row):
                if char == 'X':
                    surf.set_at((px, py), (240, 240, 240))
        _pixel_clock_cache[key] = pygame.transform.scale(surf, (7 * scale, 7 * scale))
    if s is not None:
        s.blit(_pixel_clock_cache[key], (x, y))

def draw_pixel_star(s, x, y, scale=3):
    key = scale
    if key not in _pixel_star_cache:
        grid = [
            "...X...",
            "..XXX..",
            "XXXXXXX",
            ".XXXXX.",
            "..XXX..",
            ".X.X.X.",
            "X.....X"
        ]
        surf = pygame.Surface((7, 7), pygame.SRCALPHA)
        for py, row in enumerate(grid):
            for px, char in enumerate(row):
                if char == 'X':
                    surf.set_at((px, py), (255, 215, 0))
        _pixel_star_cache[key] = pygame.transform.scale(surf, (7 * scale, 7 * scale))
    if s is not None:
        s.blit(_pixel_star_cache[key], (x, y))

def draw_mario(s, x, y, w, h, dir, anim, gnd, star, inv, power=PowerUp.NONE, ducking=False):
    if inv > 0 and (inv // 4) % 2 == 0 and not star:
        return
        
    is_big = h >= 48
    
    # 12x16 templates for small Mario
    SMALL_STAND = [
        "....RRRRR...",
        "...RRRRRRRRR",
        "...HHHSSES..",
        "..HSHSSEESES",
        "..HSHHSSESES",
        "..HHSSSSS...",
        "....RROORR..",
        "...RROOOORR.",
        "..RROOOOOORR",
        "..GGOOBOOOGG",
        "..GGOOOOOOGG",
        "...OOOOOOOO.",
        "..OOOO..OOOO",
        ".OOO......OOO",
        ".DDD......DDD",
        "DDDD......DDDD"
    ]

    SMALL_WALK1 = [
        "....RRRRR...",
        "...RRRRRRRRR",
        "...HHHSSES..",
        "..HSHSSEESES",
        "..HSHHSSESES",
        "..HHSSSSS...",
        "....RROORR..",
        "...RROOOORR.",
        "..RROOOOOORR",
        "..GGOOBOOOGG",
        "...GOOOOOOGG",
        "....OOOOOO..",
        "....OOOOOO..",
        "...OOO..OOO.",
        "..DDD....DDD",
        ".DDD......DD"
    ]

    SMALL_WALK2 = [
        "....RRRRR...",
        "...RRRRRRRRR",
        "...HHHSSES..",
        "..HSHSSEESES",
        "..HSHHSSESES",
        "..HHSSSSS...",
        "....RROORR..",
        "...RROOOORR.",
        "..RROOOOOORR",
        "..GGOOBOOOGG",
        "..GGOOOOOOG.",
        "...OOOOOO...",
        "...OOOOOO...",
        "..OOO..OOO..",
        ".DDD....DDD.",
        "DDDD....DDDD"
    ]

    SMALL_JUMP = [
        "....RRRRR...",
        "...RRRRRRRRR",
        "...HHHSSES..",
        "..HSHSSEESES",
        "..HSHHSSESES",
        "..HHSSSSS...",
        "....RROORR..",
        "...RROOOORR.",
        "..RROOOOOORR",
        "..GGOOBOOOGG",
        "..GGOOOOOOGG",
        "...OOOOOOOO.",
        "..OOOO..OOOO",
        ".DDD......OOO",
        "DDDD......DDD",
        "..........DDD"
    ]

    SMALL_DUCK = [
        "....RRRRR...",
        "...RRRRRRRRR",
        "...HHHSSES..",
        "..HSHSSEESES",
        "..HHSSSSS...",
        "....RROORR..",
        "..GGOOBOOOGG",
        ".DDDD....DDDD"
    ]

    # 12x24 templates for big Mario
    BIG_STAND = [
        "....RRRRR...",
        "...RRRRRRRRR",
        "...RRRRRRRRR",
        "...HHHSSES..",
        "..HSHSSEESES",
        "..HSHHSSESES",
        "..HSHHSSESES",
        "..HHHSSSSS..",
        "....SSSSS...",
        "....RROORR..",
        "...RRROOORRR",
        "..RRRROOOORR",
        "..GGRROOORRG",
        "..GGRROOORRG",
        "..GGBOOBOOGG",
        "...OOOOOOOO.",
        "..OOOOOOOOOO",
        "..OOOOOOOOOO",
        "..OOOO..OOOO",
        "..OOO....OOO",
        ".OOO......OOO",
        ".DDD......DDD",
        "DDDD......DDDD",
        "DDDD......DDDD"
    ]

    BIG_WALK1 = [
        "....RRRRR...",
        "...RRRRRRRRR",
        "...RRRRRRRRR",
        "...HHHSSES..",
        "..HSHSSEESES",
        "..HSHHSSESES",
        "..HSHHSSESES",
        "..HHHSSSSS..",
        "....SSSSS...",
        "....RROORR..",
        "...RRROOORRR",
        "..RRRROOOORR",
        "..GGRROOORRG",
        "...GRROOORRG",
        "...GBOOBOOGG",
        "....OOOOOOO.",
        "....OOOOOOOO",
        "....OOOOOOOO",
        "....OOO..OOO",
        "....OO....OO",
        "...OOO....OO",
        "..DDD......D",
        ".DDD........",
        "DDDD........"
    ]

    BIG_WALK2 = [
        "....RRRRR...",
        "...RRRRRRRRR",
        "...RRRRRRRRR",
        "...HHHSSES..",
        "..HSHSSEESES",
        "..HSHHSSESES",
        "..HSHHSSESES",
        "..HHHSSSSS..",
        "....SSSSS...",
        "....RROORR..",
        "...RRROOORRR",
        "..RRRROOOORR",
        "..GGRROOORRG",
        "..GGRROOORR.",
        "..GGBOOBOOG.",
        "...OOOOOOOO.",
        "..OOOOOOOOOO",
        "..OOOOOOOOOO",
        "..OOOO..OOOO",
        "..OOO....OOO",
        ".OOO......OOO",
        ".DDD......DDD",
        "DDDD......DDDD",
        "DDDD......DDDD"
    ]

    BIG_JUMP = [
        "....RRRRR...",
        "...RRRRRRRRR",
        "...RRRRRRRRR",
        "...HHHSSES..",
        "..HSHSSEESES",
        "..HSHHSSESES",
        "..HSHHSSESES",
        "..HHHSSSSS..",
        "....SSSSS...",
        "....RROORR..",
        "...RRROOORRR",
        "..RRRROOOORR",
        "..GGRROOORRG",
        "..GGRROOORRG",
        "..GGBOOBOOGG",
        "...OOOOOOOO.",
        "..OOOOOOOOOO",
        "..OOOOOOOOOO",
        "..OOOO..OOOO",
        "..OOO....OOO",
        ".DDD......OOO",
        "DDDD......DDD",
        "..........DDD",
        "..........DDD"
    ]

    BIG_DUCK = [
        "....RRRRR...",
        "...RRRRRRRRR",
        "...RRRRRRRRR",
        "...HHHSSES..",
        "..HSHSSEESES",
        "..HHHSSSSS..",
        "....SSSSS...",
        "....RROORR..",
        "..GGRROOORRG",
        "..GGBOOBOOGG",
        "...OOOOOOOO.",
        "..OOOO..OOOO",
        ".DDD......DDD",
        "DDDD......DDDD"
    ]

    # Decide height
    if ducking and gnd:
        grid_h = 14 if is_big else 8
        template = BIG_DUCK if is_big else SMALL_DUCK
    elif not gnd:
        grid_h = 24 if is_big else 16
        template = BIG_JUMP if is_big else SMALL_JUMP
    else:
        grid_h = 24 if is_big else 16
        if abs(anim) > 0.01:
            frame = int(anim * 8) % 2
            if is_big:
                template = BIG_WALK1 if frame == 0 else BIG_WALK2
            else:
                template = SMALL_WALK1 if frame == 0 else SMALL_WALK2
        else:
            template = BIG_STAND if is_big else SMALL_STAND

    # Handle rainbow flashing star mode dynamically without caching
    if star:
        surf = pygame.Surface((12, grid_h), pygame.SRCALPHA)
        t = time.time() * 12
        c_cap = c_shirt = (
            int(128 + 127 * math.sin(t)),
            int(128 + 127 * math.sin(t + 2)),
            int(128 + 127 * math.sin(t + 4))
        )
        c_skin = (255, 200, 150)
        c_hair = (80, 40, 0)
        c_overalls = (255, 255, 255)
        c_shoes = MBROWN
        c_gloves = WHITE
        color_map = {'.': (0, 0, 0, 0), 'R': c_cap, 'O': c_overalls, 'S': c_skin, 'H': c_hair, 'E': BLACK, 'G': c_gloves, 'B': GOLD, 'D': c_shoes}
        for py in range(len(template)):
            for px in range(12):
                surf.set_at((px, py), color_map[template[py][px]])
        if dir == Dir.LEFT:
            surf = pygame.transform.flip(surf, True, False)
        if s is not None:

            s.blit(pygame.transform.scale(surf, (w, h)), (x, y))
        return

    # Cache key for normal powerups/states
    frame_idx = int(anim * 8) % 2 if (abs(anim) > 0.01 and gnd) else 0
    key = (is_big, ducking, gnd, frame_idx, dir, power, w, h)
    if key not in _mario_cache:
        surf = pygame.Surface((12, grid_h), pygame.SRCALPHA)
        if power == PowerUp.FIRE:
            c_cap = c_shirt = (255, 255, 255)
            c_skin = MSKIN
            c_hair = BLACK
            c_overalls = RED
        elif power == PowerUp.SHIELD:
            c_cap = c_shirt = SHIELD_BLUE
            c_skin = MSKIN
            c_hair = MBROWN
            c_overalls = WHITE
        elif power == PowerUp.SPEED:
            c_cap = c_shirt = (255, 100, 255)
            c_skin = MSKIN
            c_hair = BLACK
            c_overalls = (0, 200, 255)
        else:
            c_cap = c_shirt = RED
            c_skin = MSKIN
            c_hair = MBROWN
            c_overalls = MBLUE
        c_shoes = MBROWN
        c_gloves = WHITE
        color_map = {'.': (0, 0, 0, 0), 'R': c_cap, 'O': c_overalls, 'S': c_skin, 'H': c_hair, 'E': BLACK, 'G': c_gloves, 'B': GOLD, 'D': c_shoes}
        for py in range(len(template)):
            for px in range(12):
                surf.set_at((px, py), color_map[template[py][px]])
        if dir == Dir.LEFT:
            surf = pygame.transform.flip(surf, True, False)
        _mario_cache[key] = pygame.transform.scale(surf, (w, h))
    if s is not None:
        s.blit(_mario_cache[key], (x, y))

def draw_shadow(s, x, y, w, alpha=80):
    alpha = max(0, min(255, alpha))
    key = (w, alpha)
    if key not in _shadow_cache:
        shadow_surf = pygame.Surface((w, max(1, w // 3)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, alpha), (0, 0, w, max(1, w // 3)))
        _shadow_cache[key] = shadow_surf
    if s is not None:
        s.blit(_shadow_cache[key], (x - w // 2, y - max(1, w // 3) // 2))

def draw_goomba(s, x, y, bob):
    key = round(bob, 1)
    if key not in _goomba_cache:
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        for py in range(2, 10):
            for px in range(2, 14):
                surf.set_at((px, py), GMBODY)
        for px in [4, 5, 10, 11]:
            surf.set_at((px, 5), WHITE)
            surf.set_at((px, 6), BLACK)
        for px in range(5, 11):
            surf.set_at((px, 8), BLACK)
        for py in range(10, 13):
            for px in range(4, 12):
                surf.set_at((px, py), GMHEAD)
        for py in range(13, 16):
            for px in range(2, 6):
                surf.set_at((px, py), BLACK)
            for px in range(10, 14):
                surf.set_at((px, py), BLACK)
        _goomba_cache[key] = pygame.transform.scale(surf, (32, 32))
    if s is not None:
        s.blit(_goomba_cache[key], (x, y + int(bob)))

def draw_koopa(s, x, y, bob):
    key = round(bob, 1)
    if key not in _koopa_cache:
        surf = pygame.Surface((16, 24), pygame.SRCALPHA)
        for py in range(8, 17):
            for px in range(3, 13):
                col = (0, 150, 0) if (px + py) % 3 == 0 else KGREEN
                surf.set_at((px, py), col)
        for py in range(2, 8):
            for px in range(6, 12):
                surf.set_at((px, py), KHEAD)
        surf.set_at((9, 4), BLACK)
        surf.set_at((9, 5), BLACK)
        for py in range(17, 22):
            for px in range(4, 7):
                surf.set_at((px, py), KHEAD)
            for px in range(9, 12):
                surf.set_at((px, py), KHEAD)
        for py in range(22, 24):
            for px in range(3, 7):
                surf.set_at((px, py), (255, 100, 0))
            for px in range(9, 13):
                surf.set_at((px, py), (255, 100, 0))
        _koopa_cache[key] = pygame.transform.scale(surf, (32, 48))
    if s is not None:
        s.blit(_koopa_cache[key], (x, y + int(bob)))

def draw_coin(s, x, y, off):
    sc = abs(math.cos(time.time() * 4 + off))
    w = max(1, int(16 * sc))
    key = (w, math.cos(time.time() * 4 + off) > 0)
    if key not in _coin_cache:
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        if key[1]:
            for py in range(8):
                for px in range(w // 2):
                    c = GOLD if (px + py) % 2 == 0 else (216, 176, 0)
                    pygame.draw.rect(surf, c, (8 - w // 2 + px * 2, py * 2, 2, 2))
        else:
            for py in range(8):
                pygame.draw.rect(surf, GOLD, (7, py * 2, 2, 2))
        _coin_cache[key] = surf
    if s is not None:
        s.blit(_coin_cache[key], (x - 8, y - 8))

def draw_brick(s, x, y, bounce=0):
    if 'base' not in _brick_cache:
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, BRICK, (0, 0, 32, 32))
        d = BRICK_D
        pygame.draw.line(surf, d, (0, 16), (32, 16), 2)
        pygame.draw.line(surf, d, (16, 0), (16, 16), 2)
        pygame.draw.line(surf, d, (8, 16), (8, 32), 2)
        pygame.draw.line(surf, d, (24, 16), (24, 32), 2)
        pygame.draw.line(surf, (100, 50, 8), (0, 31), (32, 31), 2)
        pygame.draw.line(surf, (100, 50, 8), (31, 0), (31, 32), 2)
        _brick_cache['base'] = surf
    if s is not None:
        s.blit(_brick_cache['base'], (x, y - bounce))

def draw_qblock(s, x, y, used, bounce=0):
    key = used
    if key not in _qblock_cache:
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        c1 = (136, 136, 136) if used else QBLOCK
        c2 = (96, 96, 96) if used else QBLOCK_D
        pygame.draw.rect(surf, c1, (0, 0, 32, 32))
        pygame.draw.rect(surf, c2, (0, 0, 32, 32), 2)
        if not used:
            q_points = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0),
                        (0, 1), (6, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
                        (2, 3), (3, 3), (4, 3), (3, 4), (3, 5)]
            for dx, dy in q_points:
                pygame.draw.rect(surf, BLACK, (11 + dx, 11 + dy, 2, 2))
        _qblock_cache[key] = surf
    if s is not None:
        s.blit(_qblock_cache[key], (x, y - bounce))

def draw_pipe(s, x, y, w, h):
    key = (w, h)
    if key not in _pipe_cache:
        surf = pygame.Surface((w + 8, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, PIPE_GREEN, (4, 0, w, h))
        pygame.draw.rect(surf, PIPE_L, (7, 0, 6, h))
        pygame.draw.rect(surf, PIPE_D, (4 + w - 9, 0, 6, h))
        pygame.draw.rect(surf, PIPE_GREEN, (0, 0, w + 8, 8))
        _pipe_cache[key] = surf
    if s is not None:
        s.blit(_pipe_cache[key], (x - 4, y))

def draw_piranha(s, x, y, bob):
    if 'base' not in _piranha_cache:
        surf = pygame.Surface((16, 24), pygame.SRCALPHA)
        for py in range(10, 24):
            surf.set_at((7, py), (0, 200, 0))
            surf.set_at((8, py), (0, 200, 0))
        for px, py in [(5, 14), (6, 13), (9, 13), (10, 14)]:
            surf.set_at((px, py), (0, 160, 0))
        for py in range(2, 12):
            for px in range(3, 13):
                surf.set_at((px, py), (255, 0, 80))
        for px, py in [(5, 5), (6, 6), (9, 5), (10, 6)]:
            surf.set_at((px, py), WHITE)
        for px in range(4, 12):
            surf.set_at((px, 8), BLACK)
        _piranha_cache['base'] = pygame.transform.scale(surf, (32, 48))
    if s is not None:
        s.blit(_piranha_cache['base'], (x, y + int(bob)))

def draw_mushroom(s, x, y, bob, type="super"):
    key = type
    if key not in _mushroom_cache:
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        sz = 2
        if type == "super":
            head_color = MUSH_RED
        elif type == "1up":
            head_color = (0, 200, 0)
        elif type == "shield":
            head_color = (100, 150, 255)
        elif type == "speed":
            head_color = (255, 100, 255)
        elif type == "fire":
            head_color = (255, 100, 0)
        else:
            head_color = (0, 150, 255)
        for py in range(8, 15):
            for px in range(6, 10):
                pygame.draw.rect(surf, MUSH_STEM, (px * sz, py * sz, sz, sz))
        for py in range(3, 9):
            for px in range(2, 14):
                pygame.draw.rect(surf, head_color, (px * sz, py * sz, sz, sz))
        for ex in [6, 10]:
            pygame.draw.rect(surf, BLACK, (ex * sz, 5 * sz, 2 * sz, 2 * sz))
        for sx, sy in [(4, 4), (10, 4), (7, 6)]:
            pygame.draw.rect(surf, MUSH_WHITE, (sx * sz, sy * sz, 2 * sz, 2 * sz))
        _mushroom_cache[key] = surf
    if s is not None:
        s.blit(_mushroom_cache[key], (x, y + int(bob)))

def draw_flag(s, x, y):
    pygame.draw.rect(s, (180, 180, 180), (x + 30, y, 4, 160))
    pygame.draw.line(s, WHITE, (x + 32, y), (x + 32, y + 160), 1)
    pygame.draw.circle(s, GOLD, (x + 32, y - 2), 6)
    points = [(x + 30, y + 4), (x - 10, y + 30), (x - 10, y + 60), (x + 30, y + 80)]
    pygame.draw.polygon(s, (0, 180, 0), points)

def draw_checkpoint(s, x, y, activated):
    pole_x = x + 16
    pygame.draw.rect(s, (150, 150, 150), (pole_x, y - 32, 3, 48))
    if activated:
        pygame.draw.rect(s, (0, 200, 0), (pole_x - 15, y - 30, 15, 10))
        pygame.draw.circle(s, GOLD, (pole_x + 1, y - 32), 4)
    else:
        pygame.draw.rect(s, (200, 200, 200), (pole_x - 15, y - 30, 15, 10))
        pygame.draw.circle(s, GRAY, (pole_x + 1, y - 32), 4)

def draw_bowser(s, x, y, w, h, shielded=False, inv_t=0.0, anim=0.0):
    sz = w // 12
    flash = inv_t > 0 and (int(inv_t * 15) % 2 == 0)
    
    if flash:
        c1, c2, c3, c4 = (255, 100, 100), (255, 50, 50), (255, 150, 150), (255, 200, 200)
    else:
        c1 = (0, 200, 100)      # Mechanical green body
        c2 = (150, 50, 255)     # Neon purple spikes/accents
        c3 = (255, 215, 0)      # Gold chestplate
        c4 = (255, 0, 100)      # Glowing red cyber-eyes
        
    # Draw body squares
    for py in range(3, 11):
        for px in range(2, 10):
            pygame.draw.rect(s, c1, (x + px * sz, y + py * sz, sz, sz))
            
    # Draw mechanical shell spikes (left and right)
    for px, py in [(1, 4), (1, 6), (1, 8), (10, 4), (10, 6), (10, 8)]:
        pygame.draw.rect(s, c2, (x + px * sz, y + py * sz, sz, sz))
        
    # Draw chestplate
    for py in range(5, 9):
        for px in range(4, 8):
            pygame.draw.rect(s, c3, (x + px * sz, y + py * sz, sz, sz))
            
    # Draw eyes
    for px, py in [(4, 4), (7, 4)]:
        pygame.draw.rect(s, c4, (x + px * sz, y + py * sz, sz, sz))
        
    # Draw claws
    claw_offset = int(math.sin(anim * 4) * 4)
    for px, py in [(2, 10), (3, 11), (8, 10), (9, 11)]:
        pygame.draw.rect(s, (200, 200, 200), (x + px * sz, y + py * sz + claw_offset, sz, sz))
        
    # Draw active shield ring
    if shielded:
        t = time.time() * 10
        shield_radius = int(w * 0.7)
        shield_surf = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
        alpha = int(120 + 50 * math.sin(t))
        pygame.draw.circle(shield_surf, (0, 255, 255, alpha), (shield_radius, shield_radius), shield_radius, 3)
        pygame.draw.circle(shield_surf, (0, 100, 255, alpha // 3), (shield_radius, shield_radius), shield_radius - 3)
        s.blit(shield_surf, (int(x + w//2 - shield_radius), int(y + h//2 - shield_radius)))

class HandTracker:
    def __init__(self, cam_index=0):
        self.cam_index = cam_index
        self.frame = None
        self.ok = False
        self.peace = False
        self.fist = False
        self.sx = 0.5
        self.sy = 0.5
        self.last_peace = 0.0
        self.hx = deque(maxlen=5)
        self.hy = deque(maxlen=5)
        self.initialized = False
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.hands = None

    def start_capture(self):
        with self.lock:
            if self.running: return
            self.running = True
            
        self.cap = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW if sys.platform.startswith('win') else None)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.cam_index)
            
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def stop_capture(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
            self.cap = None
        self.ok = False

    def _capture_loop(self):
        # Dynamically load MediaPipe Hands inside background thread to prevent Pygame startup lag
        if self.hands is None:
            try:
                self.hands = mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=0.45,
                    min_tracking_confidence=0.45,
                    model_complexity=0
                )
                self.initialized = True
            except Exception as e:
                print(f"[Error] MediaPipe dynamic load failed: {e}")
                self.initialized = False
                return

        while self.running:
            if not self.cap or not self.cap.isOpened():
                time.sleep(0.03)
                continue
                
            ret, f = self.cap.read()
            if not ret or f is None:
                with self.lock:
                    self.ok = False
                time.sleep(0.01)
                continue
                
            f = cv2.flip(f, 1)
            try:
                res = self.hands.process(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
                with self.lock:
                    self.frame = f
                    if res.multi_hand_landmarks:
                        lm = res.multi_hand_landmarks[0].landmark
                        tips = [lm[8], lm[12], lm[16], lm[20]]
                        pips = [lm[5], lm[9], lm[13], lm[17]]
                        
                        fingers_up = sum(1 for t, p in zip(tips, pips) if t.y < p.y - 0.03)
                        self.peace = (fingers_up == 2 and tips[0].y < pips[0].y 
                                     and tips[1].y < pips[1].y
                                     and tips[2].y > pips[2].y and tips[3].y > pips[3].y)
                        self.fist = fingers_up == 0
                        
                        wrist = lm[0]
                        self.hx.append(wrist.x)
                        self.hy.append(wrist.y)
                        
                        hx_list = list(self.hx)
                        hy_list = list(self.hy)
                        if hx_list:
                            weights = np.linspace(0.5, 1.0, len(hx_list))
                            self.sx = float(np.average(hx_list, weights=weights))
                            self.sy = float(np.average(hy_list, weights=weights))
                        else:
                            self.sx, self.sy = wrist.x, wrist.y
                        self.ok = True
                    else:
                        self.ok = False
                time.sleep(0.02)
            except Exception as e:
                print(f"[Error] HandTracker thread error: {e}")
            
    def update(self):
        pass
        
    def get_x(self):
        with self.lock:
            if not self.ok or not self.initialized: return 0.0
            return (self.sx - 0.5) * 2 * HAND_SENSITIVITY
            
    def get_y(self):
        with self.lock:
            if not self.ok or not self.initialized: return 0.0
            return (self.sy - 0.5) * 2 * HAND_SENSITIVITY
            
    def get_frame(self):
        with self.lock:
            if not self.initialized or self.frame is None: return None
            return self.frame.copy()
            
    def change_camera(self, new_index):
        if self.cam_index == new_index:
            return
            
        self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
            
        self.release()
        self.cam_index = new_index
        self.initialized = False
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        
    def release(self):
        self.running = False
        if hasattr(self, 'cap') and self.cap: 
            self.cap.release()
        try:
            if hasattr(self, 'hands') and self.hands:
                self.hands.close()
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════════════════
# ANA OYUN SINIFI (v3.2.2 - MUSH_S HATASI DÜZELTİLDİ)
# ═══════════════════════════════════════════════════════════════════════════════════



def prepopulate_all_caches(game=None):
    print("[Info] Cizim onbellekleri yukleniyor...")
    
    # Helper to pre-render coin directly into cache
    def draw_coin_direct(w, pos_cos):
        key = (w, pos_cos)
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        if pos_cos:
            for py in range(8):
                for px in range(w // 2):
                    c = GOLD if (px + py) % 2 == 0 else (216, 176, 0)
                    pygame.draw.rect(surf, c, (8 - w // 2 + px * 2, py * 2, 2, 2))
        else:
            for py in range(8):
                pygame.draw.rect(surf, GOLD, (7, py * 2, 2, 2))
        _coin_cache[key] = surf

    # Helper to pre-render Mario
    def pre_render_mario():
        for is_big in [True, False]:
            for ducking in [True, False]:
                for gnd in [True, False]:
                    for frame_idx in [0, 1]:
                        for direction in [Dir.LEFT, Dir.RIGHT]:
                            for power in [PowerUp.NONE, PowerUp.FIRE, PowerUp.SHIELD, PowerUp.SPEED]:
                                w = 32
                                if is_big:
                                    h = 28 if ducking else 48
                                else:
                                    h = 16 if ducking else 32
                                draw_mario(None, 0, 0, w, h, direction, frame_idx / 8.0, gnd, False, 0, power, ducking)

    steps = [
        ("YUKLENIYOR: Golge Efektleri...", lambda: [draw_shadow(None, 0, 0, w, alpha) for w in [24, 40, 60, 80, 112] for alpha in [30, 40, 60, 80]]),
        ("YUKLENIYOR: Goomba Karakterleri...", lambda: [draw_goomba(None, 0, 0, b / 10.0) for b in range(-20, 21)]),
        ("YUKLENIYOR: Koopa Karakterleri...", lambda: [draw_koopa(None, 0, 0, b / 10.0) for b in range(-20, 21)]),
        ("YUKLENIYOR: Boru Canavarlari...", lambda: draw_piranha(None, 0, 0, 0)),
        ("YUKLENIYOR: Altin Animasyonlari...", lambda: [draw_coin_direct(w, pos_cos) for w in range(1, 17) for pos_cos in [True, False]]),
        ("YUKLENIYOR: Mucize Mantarlar...", lambda: [draw_mushroom(None, 0, 0, 0, t) for t in ["super", "1up", "shield", "speed", "fire"]]),
        ("YUKLENIYOR: Tuglalar ve Bloklar...", lambda: [draw_brick(None, 0, 0, 0), draw_qblock(None, 0, 0, False, 0), draw_qblock(None, 0, 0, True, 0)]),
        ("YUKLENIYOR: Yesil Borular...", lambda: [draw_pipe(None, 0, 0, w, h) for w in [64, 96, 128] for h in [32, 64, 96]]),
        ("YUKLENIYOR: Arayuz Ogeleri...", lambda: [draw_pixel_heart(None, 0, 0, 3), draw_pixel_clock(None, 0, 0, 3), draw_pixel_star(None, 0, 0, 3), draw_menu_mushroom(None, 0, 0, 28)]),
        ("YUKLENIYOR: Mario Karakteri...", lambda: pre_render_mario())
    ]
    
    total_steps = len(steps)
    for idx, (label, action) in enumerate(steps):
        action()
        if game is not None and game.s is not None:
            # Draw professional loading screen
            game.s.fill((12, 12, 20))
            
            # Draw double-line retro dialog box in the center
            dw, dh = 500, 160
            dx, dy = SW // 2 - dw // 2, SH // 2 - dh // 2
            pygame.draw.rect(game.s, (0, 0, 0), (dx, dy, dw, dh))
            pygame.draw.rect(game.s, WHITE, (dx, dy, dw, dh), 4)
            pygame.draw.rect(game.s, (0, 0, 0), (dx + 6, dy + 6, dw - 12, dh - 12))
            pygame.draw.rect(game.s, WHITE, (dx + 6, dy + 6, dw - 12, dh - 12), 1)
            
            # Text label
            draw_retro_text(game.s, "SUPER MARIO BROS - ULTIMATE", game.fs, dx + 40, dy + 25, GOLD, BLACK)
            draw_retro_text(game.s, label, game.ft, dx + 40, dy + 65, WHITE, BLACK)
            
            # Progress bar
            bar_w = dw - 80
            bar_h = 16
            bar_x = dx + 40
            bar_y = dy + 105
            progress = (idx + 1) / total_steps
            pygame.draw.rect(game.s, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(game.s, GREEN, (bar_x, bar_y, int(bar_w * progress), bar_h))
            pygame.draw.rect(game.s, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
            
            pygame.display.flip()
            pygame.time.wait(20)  # Subtle delay to show progress beautifully
            
    print("[OK] Tum onbellekler basariyla yuklendi!")

class MarioUltimate:
    def __init__(self):
        print("\n" + "=" * 70)
        print("  SUPER MARIO BROS - ULTIMATE EDITION v3.2.2")
        print("  MUSH_S Hatasi Duzeltildi - Tum Hatalar Giderildi")
        print("=" * 70 + "\n")
        
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        SoundGenerator.pre_generate_all()
        
        self.s = pygame.display.set_mode((SW, SH), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("SUPER MARIO BROS - ULTIMATE v3.2.2")
        
        icon = pygame.Surface((32, 32))
        icon.fill(MRED)
        pygame.display.set_icon(icon)
        
        self.clock = pygame.time.Clock()
        
        self.fl = pygame.font.Font(None, 100)
        self.fb = pygame.font.Font(None, 64)
        self.fm = pygame.font.Font(None, 48)
        self.fs = pygame.font.Font(None, 32)
        self.ft = pygame.font.Font(None, 20)
        
        self.control_mode = 0  # 0: Keyboard, 1: Hand Tracking
        self.selected_cam_index = 0
        self.available_cams = [0]
        self.hand = None
        self.mouse_clicked = False
        
        self.state = State.MENU
        self.p: Optional[Player] = None
        self.blocks: List[Block] = []
        self.enemies: List[Enemy] = []
        self.coins: List[Coin] = []
        self.mushrooms: List[Mushroom] = []
        self.particles: List[Particle] = []
        self.score_popups: List[ScorePopup] = []
        self.fireballs: List[Fireball] = []
        self.checkpoints: List[Checkpoint] = []
        self.screen_effects: List[ScreenEffect] = []
        
        self.score = 0
        self.coins_c = 0
        self.lives = LIVES
        self.kills = 0
        
        self.cx = 0.0
        self.target_cx = 0.0
        self.gt = 0.0
        self.st = 0.0
        self.dt = 0.016
        
        self.shake = 0.0
        self.sx = 0.0
        self.sy = 0.0
        self.transition_alpha = 0
        self.transition_dir = 0
        self.slow_mo = 1.0
        self.weather_timer = 0
        self.level = 1
        self.boss = None
        self.boss_triggered = False
        self.fever_mode = False
        self.fever_t = 0.0
        self.last_fire_t = 0.0
        
        self.flag_reached = False
        self.flag_timer = 0
        self.last_checkpoint: Optional[Checkpoint] = None
        
        self.sound_cooldown = {}
        
        self.menu_time = 0
        self.menu_selected = 0
        self.pause_selected = 0
        self.over_selected = 0
        
        self.clouds = [(random.randint(0, SW*2), random.randint(20, 200), 
                       random.randint(60, 140), random.uniform(0.05, 0.2)) for _ in range(12)]
        self.hills_far = [(random.randint(0, WW), random.randint(GY-60, GY-30), 
                          random.randint(100, 180), random.randint(20, 40)) for _ in range(20)]
        self.hills_near = [(random.randint(0, WW), random.randint(GY-80, GY-50), 
                           random.randint(60, 120), random.randint(25, 45)) for _ in range(15)]
        self.mountains = [(random.randint(0, WW), random.randint(GY-140, GY-90), 
                          random.randint(150, 250), random.randint(60, 100)) for _ in range(8)]
        # Reusable surfaces to prevent garbage collection lag
        self.black_overlay = pygame.Surface((SW, SH))
        self.black_overlay.fill((0, 0, 0))
        
        self.vignette_surf = pygame.Surface((SW, SH), pygame.SRCALPHA)
        for i in range(5):
            alpha = int(30 * (i/5))
            pygame.draw.rect(self.vignette_surf, (0, 0, 0, alpha),
                           (i*8, i*8, SW-i*16, SH-i*16), 8)
                           
        self.flash_overlay = pygame.Surface((SW, SH))
        
        prepopulate_all_caches(self)
        self.stars = [(random.randint(0, SW), random.randint(0, SH//2), 
                      random.uniform(0.5, 2.0), random.uniform(0.5, 1.5)) for _ in range(50)]
        
        self.hs = 0
        self.max_combo_record = 0
        
        # Default settings configurations
        self.master_volume = 0.7
        self.weather = Weather.CLEAR
        self.difficulty = Difficulty.NORMAL
        self.fullscreen = False
        self.show_fps = False
        self.control_mode = 0
        self.selected_cam_index = 0

        try:
            with open(SCORE_F, 'r') as f:
                data = json.load(f)
                self.hs = data.get('hs', 0)
                self.max_combo_record = data.get('max_combo', 0)
                
                # Load persistent settings if available
                if 'volume' in data: self.master_volume = data['volume']
                if 'weather' in data: self.weather = Weather(data['weather'])
                if 'difficulty' in data: self.difficulty = Difficulty(data['difficulty'])
                if 'fullscreen' in data: self.fullscreen = data['fullscreen']
                if 'show_fps' in data: self.show_fps = data['show_fps']
                if 'control_mode' in data: self.control_mode = data['control_mode']
                if 'selected_cam_index' in data: self.selected_cam_index = data['selected_cam_index']
        except:
            pass
        
        # Apply startup settings
        self.hand = HandTracker(self.selected_cam_index)
        if self.control_mode == 1:
            self.hand.start_capture()

        if self.fullscreen:
            try: pygame.display.toggle_fullscreen()
            except: pass
            
        bw = 380; bh = 65; bx = SW//2 - bw//2
        self.menu_buttons = [
            Button(bx, 270, bw, bh, "OYUNA BASLA", "start", icon="▶"),
            Button(bx, 350, bw, bh, "KONTROLLER", "controls", icon="⌨"),
            Button(bx, 430, bw, bh, "AYARLAR", "settings", icon="⚙"),
            Button(bx, 510, bw, bh, "CIKIS", "quit", icon="✕"),
        ]
        
        self.pause_buttons = [
            Button(SW//2-190, 280, 380, 65, "DEVAM ET", "resume", icon="▶"),
            Button(SW//2-190, 360, 380, 65, "YENIDEN BASLAT", "restart", icon="↻"),
            Button(SW//2-190, 440, 380, 65, "ANA MENU", "menu", icon="⌂"),
        ]
        
        self.over_buttons = [
            Button(SW//2-190, 350, 380, 65, "YENIDEN DENE", "restart", icon="↻"),
            Button(SW//2-190, 430, 380, 65, "ANA MENU", "menu", icon="⌂"),
        ]
        
        self._init_settings_buttons()
    
    def _init_settings_buttons(self):
        bw = 500; bh = 50; bx = SW//2 - bw//2
        start_y = 130; gap = 55
        
        self.settings_buttons = [
            SettingsButton(bx, start_y, bw, bh, "Ses Seviyesi", "volume",
                          int(self.master_volume * 100), 0, 100, 10),
            SettingsButton(bx, start_y + gap, bw, bh, "Hava Durumu", "weather",
                          0, options=[w.name for w in Weather]),
            SettingsButton(bx, start_y + gap*2, bw, bh, "Zorluk", "difficulty",
                          1, options=[d.name for d in Difficulty]),
            SettingsButton(bx, start_y + gap*3, bw, bh, "Tam Ekran", "fullscreen",
                          0, options=["Kapali", "Acik"]),
            SettingsButton(bx, start_y + gap*4, bw, bh, "FPS Goster", "show_fps",
                          0, options=["Kapali", "Acik"]),
            SettingsButton(bx, start_y + gap*5, bw, bh, "Kontrol Modu", "control_mode",
                          0, options=["Klavye", "El Takibi"]),
            SettingsButton(bx, start_y + gap*6, bw, bh, "Kamera Sec", "camera",
                          0, options=["Kamera 0"]),
        ]
        
        self.settings_selected = 0
        self.settings_back_btn = Button(SW//2-120, SH-90, 240, 55, "KAYDET VE DON", "back",
                                       (0, 150, 0), (0, 200, 0), WHITE, 35)
    
    def _enter_settings(self):
        self.available_cams = [0, 1, 2, 3]
        
        # Re-build buttons with scanned cameras
        bw = 500; bh = 50; bx = SW//2 - bw//2
        start_y = 130; gap = 55
        
        self.settings_buttons = [
            SettingsButton(bx, start_y, bw, bh, "Ses Seviyesi", "volume",
                          int(self.master_volume * 100), 0, 100, 10),
            SettingsButton(bx, start_y + gap, bw, bh, "Hava Durumu", "weather",
                          self.weather.value, options=[w.name for w in Weather]),
            SettingsButton(bx, start_y + gap*2, bw, bh, "Zorluk", "difficulty",
                          self.difficulty.value, options=[d.name for d in Difficulty]),
            SettingsButton(bx, start_y + gap*3, bw, bh, "Tam Ekran", "fullscreen",
                          1 if self.fullscreen else 0, options=["Kapali", "Acik"]),
            SettingsButton(bx, start_y + gap*4, bw, bh, "FPS Goster", "show_fps",
                          1 if self.show_fps else 0, options=["Kapali", "Acik"]),
            SettingsButton(bx, start_y + gap*5, bw, bh, "Kontrol Modu", "control_mode",
                          self.control_mode, options=["Klavye", "El Takibi"]),
            SettingsButton(bx, start_y + gap*6, bw, bh, "Kamera Sec", "camera",
                          0, options=[f"Kamera {idx}" for idx in self.available_cams]),
        ]
        
        # Select active camera in the options list
        try:
            cur_idx = self.available_cams.index(self.selected_cam_index)
            self.settings_buttons[6].value = cur_idx
        except ValueError:
            self.settings_buttons[6].value = 0
            
        self.state = State.SETTINGS
        
    def _apply_settings(self):
        for sb in self.settings_buttons:
            if sb.key == "volume":
                self.master_volume = sb.value / 100.0
            elif sb.key == "weather":
                self.weather = Weather(sb.value)
                self.weather_timer = 999
            elif sb.key == "difficulty":
                self.difficulty = Difficulty(sb.value)
            elif sb.key == "fullscreen":
                new_fullscreen = sb.value == 1
                if new_fullscreen != self.fullscreen:
                    pygame.display.toggle_fullscreen()
                    self.fullscreen = new_fullscreen
            elif sb.key == "show_fps":
                self.show_fps = sb.value == 1
            elif sb.key == "control_mode":
                self.control_mode = sb.value
            elif sb.key == "camera":
                self.selected_cam_index = self.available_cams[sb.value]

        # Sync hand tracker camera based on final settings values
        if self.control_mode == 1:
            if self.hand is None:
                self.hand = HandTracker(self.selected_cam_index)
            elif self.hand.cam_index != self.selected_cam_index:
                self.hand.change_camera(self.selected_cam_index)
            self.hand.start_capture()
        else:
            if self.hand is not None:
                self.hand.stop_capture()

        # Save settings persistently to JSON file
        try:
            with open(SCORE_F, 'w') as f:
                json.dump({
                    'hs': self.hs,
                    'max_combo': self.max_combo_record,
                    'volume': self.master_volume,
                    'weather': self.weather.value,
                    'difficulty': self.difficulty.value,
                    'fullscreen': self.fullscreen,
                    'show_fps': self.show_fps,
                    'control_mode': self.control_mode,
                    'selected_cam_index': self.selected_cam_index,
                    'date': time.strftime('%Y-%m-%d %H:%M:%S')
                }, f)
        except:
            pass
    
    def _can_play_sound(self, sound_name, cooldown=0.08):
        now = time.time()
        if sound_name in self.sound_cooldown:
            if now - self.sound_cooldown[sound_name] < cooldown:
                return False
        self.sound_cooldown[sound_name] = now
        return True
    
    def _build(self):
        T, G, W = TILE, GY, WW
        self.blocks.clear(); self.enemies.clear(); self.coins.clear()
        self.mushrooms.clear(); self.particles.clear(); self.score_popups.clear()
        self.fireballs.clear(); self.checkpoints.clear(); self.screen_effects.clear()
        
        self.boss = None
        self.boss_triggered = False
        self.fever_mode = False
        self.fever_t = 0.0
        
        for x in range(0, W, T):
            self.blocks.append(Block(x, G, T, T, BType.GRASS))
            self.blocks.append(Block(x, G+T, T, T, BType.GROUND))
        
        block_configs = [
            (400,-120,5), (750,-100,4), (1100,-160,6), (1500,-130,5),
            (1900,-200,5), (2400,-110,6), (2800,-220,4), (3300,-140,6),
            (3800,-180,5), (4300,-130,4), (4900,-240,6), (5500,-150,5),
            (6100,-200,7), (6700,-120,4), (7200,-180,6)
        ]
        # Expand block configurations up to 15900 with rich and dense options
        for x in range(7800, 15900, 450):
            yo = random.choice([-100, -140, -180, -220])
            w = random.randint(5, 9)
            block_configs.append((x, yo, w))
        
        for px, yo, w in block_configs:
            bt = random.choice([BType.QUESTION]*4+[BType.BRICK]*6)
            for i in range(w):
                b = Block(px+i*T, G+yo, T, T, bt)
                if bt == BType.QUESTION:
                    r = random.random()
                    if r < 0.30: b.item = 'coin'
                    elif r < 0.45: b.item = 'mushroom'
                    elif r < 0.58: b.item = 'fire'   # Fire Flower!
                    elif r < 0.70: b.item = 'star'
                    elif r < 0.80: b.item = 'shield'
                    elif r < 0.90: b.item = 'speed'
                    else: b.item = '1up'
                self.blocks.append(b)
                
                # Spawn a beautiful coin line above every brick block configuration
                if bt == BType.BRICK and random.random() < 0.4:
                    self.coins.append(Coin(px+i*T + 16, G+yo - 40, off=random.uniform(0, 6.28)))
        
        hidden_positions = [(600, -80), (1600, -120), (3200, -100), (5200, -150)]
        for x in range(6500, 15900, 1200):
            hidden_positions.append((x, random.choice([-80, -120, -160])))
        for hx, hy in hidden_positions:
            self.blocks.append(Block(hx, G+hy, T, T, BType.HIDDEN, item='coin'))
        
        pipes_px = [850, 1800, 3000, 4200, 5700, 6800]
        for x in range(8000, 15900, 1200):
            pipes_px.append(x)
        for px in pipes_px:
            for h in range(2):
                self.blocks.append(Block(px, G-T*(h+1), T*2, T, BType.PIPE))
            # Spawning Piranha Plant Pipe Monsters centered at px+16, G-T*2
            self.enemies.append(Enemy(x=px + 16, y=G - T*2, w=32, h=32, type=EType.PIRANHA, vx=0))
        
        pits = [(1150,5), (2450,5), (3700,5), (5000,6), (6300,5)]
        for x in range(7600, 15800, 1500):
            pits.append((x, random.choice([4, 5, 6])))
        for hx, hw in pits:
            self.blocks = [b for b in self.blocks if not(
                b.type in [BType.GROUND, BType.GRASS] and hx <= b.x < hx+hw*T)]
            
            # Spawn beautiful parabolic arcs of coins over every pit gap!
            num_pit_coins = hw + 2
            for c_idx in range(num_pit_coins):
                t_val = c_idx / (num_pit_coins - 1)
                cx = hx - 16 + t_val * (hw * T + 32)
                # Parabolic peak
                cy = G - 80 - math.sin(t_val * math.pi) * 110
                self.coins.append(Coin(cx, cy, off=random.uniform(0, 6.28)))
        
        enemy_count = {Difficulty.EASY: 40, Difficulty.NORMAL: 80, Difficulty.HARD: 120}
        for _ in range(enemy_count[self.difficulty]):
            ex = random.randint(600, W-1000)
            enemy_type = random.choices([EType.GOOMBA, EType.KOOPA], weights=[7, 3])[0]
            speed_mult = {Difficulty.EASY: 0.7, Difficulty.NORMAL: 1.0, Difficulty.HARD: 1.4}
            self.enemies.append(Enemy(ex, G-T, 32, 32, enemy_type, 
                                     random.uniform(1.0, 3.0) * speed_mult[self.difficulty]))
        
        # Add general scattered exploration coins
        for _ in range(400):
            cx = random.randint(300, W-600)
            cy = random.randint(G-420, G-60)
            # Ensure not colliding with any block
            self.coins.append(Coin(cx, cy, off=random.uniform(0, 6.28)))
        
        checkpoints_px = [2000, 4500, 6500]
        for x in range(8500, 15500, 2000):
            checkpoints_px.append(x)
        for cpx in checkpoints_px:
            self.checkpoints.append(Checkpoint(cpx, G-64))
        
        self.blocks.append(Block(W-500, G-160, 32, 160, BType.FLAG))
        self.flag_reached = False
        self.flag_timer = 0
        
        start_x = 100
        if self.last_checkpoint:
            start_x = self.last_checkpoint.x
        
        self.p = Player(start_x, G - 48, lives=self.lives)
        self.p.y = float(G - 48)
        self.p.vy = 0.0
        self.p.vx = 0.0
        self.p.ground = True
        self.p.jumps = self.p.max_jumps
        self.p.was_on_ground = True
        
        self.cx = self.p.x - SW * 0.35
        self.target_cx = self.cx
        
        player_rect = self.p.rect
        grounded = False
        for b in self.blocks:
            if b.type in [BType.GROUND, BType.GRASS]:
                if abs(b.x - self.p.x) < 200 and abs(b.y - G) < 10:
                    if player_rect.colliderect(b.rect):
                        self.p.y = float(b.y - self.p.h)
                        grounded = True
                        break
        
        if not grounded:
            self.p.y = float(G - 48)
        
        self.p.ground = True
        self.p.vy = 0.0
        
        print(f"  Oyun dunyasi olusturuldu. Mario X:{self.p.x:.0f} Y:{self.p.y:.0f} Ground:{self.p.ground}")
    
    def _spawn_jump_particles(self, x, y):
        for _ in range(8):
            self.particles.append(Particle(
                x, y,
                random.uniform(-3, 3), random.uniform(-2, 0),
                random.uniform(0.2, 0.4), random.uniform(0.2, 0.4),
                3, 3, 1,
                (255, 255, 200), (255, 255, 200),
                0.05
            ))
    
    def _add_score_popup(self, x, y, text, color, pulse=False):
        self.score_popups.append(ScorePopup(x, y, text, color, 
                                           max_life=1.0 if not pulse else 1.5,
                                           pulse=pulse))
    
    def _add_screen_effect(self, effect_type, intensity=1.0, duration=0.5, color=(255,255,255)):
        self.screen_effects.append(ScreenEffect(effect_type, intensity, duration, duration, color))
    
    def _input(self):
        if self.state != State.PLAY or self.p is None: return
        p, h = self.p, self.hand
        
        move_input = 0.0
        duck_input = False
        
        if self.control_mode == 1 and h is not None and h.ok:
            nx = h.get_x()
            ny = h.get_y()
            move_input = nx
            duck_input = ny > 0.5
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_input = -1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_input = 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            duck_input = True
        
        p.ducking = duck_input and p.ground
        
        if abs(move_input) < 0.04:
            p.vx *= FRICTION if p.ground else AIR_FRICTION
            if abs(p.vx) < 0.1:
                p.vx = 0.0
        else:
            target_speed = move_input * (MAX_RUN_SPD if p.speed_boost else MAX_SPD)
            acc = RUN_ACC if abs(p.vx) > MAX_SPD * 0.7 else ACC
            
            if p.ground:
                p.vx += (target_speed - p.vx) * acc * 0.15
            else:
                p.vx += (target_speed - p.vx) * acc * 0.08
            
            if move_input > 0.04:
                p.dir = Dir.RIGHT
            elif move_input < -0.04:
                p.dir = Dir.LEFT
        
        max_spd = MAX_RUN_SPD if p.speed_boost else MAX_SPD
        if p.star: max_spd *= 1.3
        p.vx = max(-max_spd, min(max_spd, p.vx))
        
        if abs(p.vx) > MAX_SPD * 0.9 and p.ground:
            p.dash_charge = min(1.0, p.dash_charge + 0.02)
        else:
            p.dash_charge = max(0.0, p.dash_charge - 0.05)
        
        now = time.time()
        jump_pressed = False
        
        if self.control_mode == 1 and h is not None and h.ok and h.peace and now - h.last_peace > GESTURE_CD:
            jump_pressed = True
            h.last_peace = now
        
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            jump_pressed = True
        
        if jump_pressed and p.jumps > 0:
            jump_power = JUMP
            if p.speed > MAX_SPD * 0.8:
                jump_power = HIGH_JUMP
            if p.dash_charge > 0.8:
                jump_power *= 1.1
            
            p.vy = jump_power
            p.jumps -= 1
            p.ground = False
            
            if p.jumps == 0:
                if self._can_play_sound('jump'):
                    SoundGenerator.jump_sound(volume=self.master_volume * 0.4)
            else:
                if self._can_play_sound('double_jump'):
                    SoundGenerator.double_jump_sound(volume=self.master_volume * 0.4)
            
            self._spawn_jump_particles(p.x + p.w//2, p.y + p.h)
            p.perfect_jump_timer = 0.15
        
        if not jump_pressed and p.vy < -4:
            p.vy *= 0.85
        
        if duck_input and not p.ground and p.vy > 0:
            p.ground_pound = True
            p.vy = 18
            
        # Shoot Fireball controls
        fire_pressed = False
        if keys[pygame.K_x] or keys[pygame.K_f] or keys[pygame.K_z]:
            fire_pressed = True
        if self.control_mode == 1 and h is not None and h.ok and h.fist:
            fire_pressed = True
            
        if fire_pressed and p.power == PowerUp.FIRE and now - self.last_fire_t > 0.35:
            self.last_fire_t = now
            if len(self.fireballs) < 5:
                fb_vx = 9 if p.dir == Dir.RIGHT else -9
                self.fireballs.append(Fireball(
                    p.x + p.w//2, p.y + p.h//2 - 4, fb_vx, -3
                ))
                if self._can_play_sound('bump'):
                    SoundGenerator.bump_sound(volume=self.master_volume * 0.4)
    
    def _update(self, dt):
        if self.state != State.PLAY or self.p is None: return
        p = self.p
        dt *= self.slow_mo
        
        p.was_on_ground = p.ground
        
        # 1. Horizontal Sub-stepped movement and collision resolution
        dx = p.vx * dt * 60
        steps_x = max(1, int(abs(dx) // 8) + 1)
        sub_dx = dx / steps_x
        
        for _ in range(steps_x):
            p.x += sub_dx
            p.x = max(0, min(p.x, WW - p.w))
            pr = p.rect
            
            for b in self.blocks:
                if b.type in [BType.GROUND, BType.GRASS]:
                    if abs(b.x - p.x) > 200: continue
                else:
                    if abs(b.x - p.x) > 150: continue
                if b.type == BType.HIDDEN: continue
                
                if pr.colliderect(b.rect):
                    ot = pr.bottom - b.rect.top
                    ob = b.rect.bottom - pr.top
                    ol = pr.right - b.rect.left
                    oR = b.rect.right - pr.left
                    mo = min(ot, ob, ol, oR)
                    
                    if mo == ol and p.vx > 0:
                        p.x = b.x - p.w
                        p.vx = 0
                        break
                    elif mo == oR and p.vx < 0:
                        p.x = b.x + b.w
                        p.vx = 0
                        break
                        
        if abs(p.vx) > 1:
            p.trail.append((p.x + p.w//2, p.y + p.h//2, time.time()))
            
        p.ground = False
        p.ground_pound = False
        
        # 2. Vertical Sub-stepped movement and collision resolution
        p.vy += GRAV * dt * 60
        if p.vy > 18: p.vy = 18
        
        dy = p.vy * dt * 60
        steps_y = max(1, int(abs(dy) // 8) + 1)
        sub_dy = dy / steps_y
        
        for _ in range(steps_y):
            p.y += sub_dy
            pr = p.rect
            collision_resolved = False
            
            for b in self.blocks:
                if b.type in [BType.GROUND, BType.GRASS]:
                    if abs(b.x - p.x) > 200: continue
                else:
                    if abs(b.x - p.x) > 150: continue
                
                if b.type == BType.HIDDEN and not b.hidden:
                    # Hidden blocks can only be hit from below
                    if pr.colliderect(b.rect) and p.vy < 0:
                        b.hidden = True
                        b.type = BType.QUESTION
                        b.item = 'coin'
                        self.coins_c += 2 if self.fever_mode else 1
                        self.score += COIN_S * (2 if self.fever_mode else 1)
                        if self._can_play_sound('coin'):
                            SoundGenerator.coin_sound(volume=self.master_volume * 0.5)
                        self._add_score_popup(b.x, b.y, f"+{COIN_S * (2 if self.fever_mode else 1)}", GOLD)
                        b.bounce = 10; b.bounce_t = 0.12
                        p.y = b.y + b.h
                        p.vy = 2
                        collision_resolved = True
                        break
                    continue
                
                if pr.colliderect(b.rect):
                    ot = pr.bottom - b.rect.top
                    ob = b.rect.bottom - pr.top
                    ol = pr.right - b.rect.left
                    oR = b.rect.right - pr.left
                    mo = min(ot, ob, ol, oR)
                    
                    if mo == ot and p.vy >= 0:
                        p.y = b.y - p.h
                        p.vy = 0
                        p.ground = True
                        p.jumps = p.max_jumps
                        p.ground_pound = False
                        collision_resolved = True
                        
                        if b.type == BType.QUESTION and not b.used:
                            b.used = True
                            b.bounce = 8; b.bounce_t = 0.1
                            if self._can_play_sound('bump'):
                                SoundGenerator.bump_sound(volume=self.master_volume * 0.3)
                            
                            if b.item == 'coin':
                                self.coins_c += 2 if self.fever_mode else 1
                                self.score += COIN_S * (2 if self.fever_mode else 1)
                                if self._can_play_sound('coin'):
                                    SoundGenerator.coin_sound(volume=self.master_volume * 0.5)
                                self._add_score_popup(b.x, b.y, f"+{COIN_S * (2 if self.fever_mode else 1)}", GOLD)
                            elif b.item == 'mushroom':
                                self.mushrooms.append(Mushroom(b.x, b.y-32, type="super"))
                                if self._can_play_sound('powerup'):
                                    SoundGenerator.powerup_sound(volume=self.master_volume * 0.5)
                            elif b.item == 'fire':
                                self.mushrooms.append(Mushroom(b.x, b.y-32, type="fire"))
                                if self._can_play_sound('powerup'):
                                    SoundGenerator.powerup_sound(volume=self.master_volume * 0.5)
                            elif b.item == 'shield':
                                self.mushrooms.append(Mushroom(b.x, b.y-32, type="shield"))
                                if self._can_play_sound('powerup'):
                                    SoundGenerator.powerup_sound(volume=self.master_volume * 0.5)
                            elif b.item == 'speed':
                                self.mushrooms.append(Mushroom(b.x, b.y-32, type="speed"))
                                if self._can_play_sound('powerup'):
                                    SoundGenerator.powerup_sound(volume=self.master_volume * 0.5)
                            elif b.item == 'star':
                                p.star = True; p.star_t = STAR_T
                                if self._can_play_sound('star'):
                                    SoundGenerator.star_sound(volume=self.master_volume * 0.4)
                                self._add_score_popup(b.x, b.y, "STAR!", GOLD, True)
                            elif b.item == '1up':
                                p.lives += 1
                                if self._can_play_sound('powerup'):
                                    SoundGenerator.powerup_sound(volume=self.master_volume * 0.5)
                                self._add_score_popup(b.x, b.y, "1UP!", GREEN, True)
                        
                        elif b.type == BType.CHECKPOINT:
                            checkpoint = next((cp for cp in self.checkpoints if abs(cp.x - b.x) < 10), None)
                            if checkpoint and not checkpoint.activated:
                                checkpoint.activated = True
                                self.last_checkpoint = checkpoint
                                if self._can_play_sound('checkpoint'):
                                    SoundGenerator.checkpoint_sound(volume=self.master_volume * 0.5)
                                self._add_score_popup(b.x, b.y, "SAVE", GOLD)
                        
                        elif b.type == BType.FLAG and not self.flag_reached:
                            self.flag_reached = True
                            self.flag_timer = 3.0
                            if self._can_play_sound('powerup'):
                                SoundGenerator.powerup_sound(volume=self.master_volume * 0.5)
                            self.score += 5000
                            self._add_score_popup(b.x, b.y, "+5000", GOLD, True)
                            self._add_screen_effect("flash", 0.8, 0.5, GOLD)
                        break
                    
                    elif mo == ob and p.vy < 0:
                        p.y = b.y + b.h
                        p.vy = 0
                        collision_resolved = True
                        
                        if b.type == BType.BRICK:
                            if p.big or p.ground_pound:
                                self.blocks.remove(b)
                                if self._can_play_sound('bump'):
                                    SoundGenerator.bump_sound(volume=self.master_volume * 0.45)
                                self.score += 100 * (2 if self.fever_mode else 1)
                                self._add_score_popup(b.x, b.y, f"+{100 * (2 if self.fever_mode else 1)}", GOLD, True)
                                self.shake = 18
                                # Enhanced brick debris with extra fragments, longer life, smoke, and flames
                                for _ in range(24):
                                    self.particles.append(Particle(
                                        x=b.x + random.randint(0, 32),
                                        y=b.y + random.randint(0, 16),
                                        vx=random.uniform(-7, 7),
                                        vy=random.uniform(-11, -2),
                                        life=random.uniform(0.8, 1.4),
                                        max_life=1.4,
                                        size=random.randint(6, 12),
                                        start_size=random.randint(6, 12),
                                        end_size=2,
                                        color=random.choice([BRICK, BRICK_D, (255, 100, 0), (255, 200, 0)]),
                                        end_color=random.choice([(100, 100, 100), BRICK_D]),
                                        gravity=0.28,
                                        shape="rect",
                                        angle=random.uniform(0, 360),
                                        angular_velocity=random.uniform(-15, 15),
                                        bounces=random.choice([1, 2, 3])
                                    ))
                            else:
                                b.bounce = 5; b.bounce_t = 0.08
                                if self._can_play_sound('bump'):
                                    SoundGenerator.bump_sound(volume=self.master_volume * 0.3)
                        break
            if collision_resolved:
                break
                
        for b in self.blocks:
            if b.bounce_t > 0:
                b.bounce_t -= dt
                b.bounce = int(10 * (b.bounce_t / 0.12))
            else:
                b.bounce = 0
        
        p.x = max(0, min(p.x, WW - p.w))
        
        # ACİL DURUM ZEMİNE OTURTMA - DÜZELTİLDİ
        if not p.ground and p.vy >= 0 and p.y >= GY - p.h - 5 and p.y <= GY - p.h + 20:
            for b in self.blocks:
                if b.type in [BType.GROUND, BType.GRASS]:
                    if b.x <= p.x + p.w - 4 and p.x + 4 <= b.x + b.w and abs(b.y - GY) < 5:
                        if abs(p.y + p.h - b.y) < 25:
                            p.y = b.y - p.h
                            p.vy = 0
                            p.ground = True
                            p.jumps = p.max_jumps
                            break
        
        if p.y > SH + 500:
            if self._can_play_sound('death', 0.5):
                SoundGenerator.death_sound(volume=self.master_volume * 0.5)
            self._die()
        
        self.target_cx = p.x - SW * 0.35
        self.cx += (self.target_cx - self.cx) * 0.08
        
        if p.star:
            p.star_t -= dt * 60
            if p.star_t <= 0: p.star = False
        if p.shield:
            p.shield_t -= dt * 60
            if p.shield_t <= 0: p.shield = False
        if p.speed_boost:
            p.speed_t -= dt * 60
            if p.speed_t <= 0: p.speed_boost = False
        if p.inv > 0: p.inv -= dt * 60
        if p.perfect_jump_timer > 0: p.perfect_jump_timer -= dt
        
        if p.combo_timer > 0:
            p.combo_timer -= dt
            if p.combo_timer <= 0: p.combo = 0
        
        for e in self.enemies:
            if not e.alive: continue
            if e.dead:
                e.dead_t -= dt
                e.alive = e.dead_t > 0
                continue
            
            if e.type == EType.PIRANHA:
                e.anim += dt * 3
                cycle = e.anim % 16
                base_y = GY - 64
                if cycle < 4:
                    e.y = base_y + 32 - (cycle / 4) * 64
                elif cycle < 8:
                    e.y = base_y - 32
                elif cycle < 12:
                    e.y = base_y - 32 + ((cycle - 8) / 4) * 64
                else:
                    e.y = base_y + 32
            else:
                # 1. Apply gravity to walking enemies
                e.vy += GRAV * dt * 60
                if e.vy > 12: e.vy = 12
                
                # 2. Horizontal movement and block collision
                e.x += e.vx * dt * 60
                e_rect = e.rect
                for b in self.blocks:
                    if b.type in [BType.GROUND, BType.GRASS, BType.BRICK, BType.QUESTION, BType.PIPE]:
                        if e_rect.colliderect(b.rect):
                            if e.vx > 0:
                                e.x = b.rect.left - e.w
                                e.vx = -e.vx
                            elif e.vx < 0:
                                e.x = b.rect.right
                                e.vx = -e.vx
                            e_rect = e.rect
                
                # 3. Vertical movement and block collision
                e.y += e.vy * dt * 60
                e_rect = e.rect
                for b in self.blocks:
                    if b.type in [BType.GROUND, BType.GRASS, BType.BRICK, BType.QUESTION, BType.PIPE]:
                        if e_rect.colliderect(b.rect):
                            if e.vy > 0: # Falling
                                prev_y = e.y - e.vy * dt * 60
                                if prev_y + e.h <= b.rect.top + 4:
                                    if b.rect.left < e.x + e.w - 6 and e.x + 6 < b.rect.right:
                                        e.y = b.rect.top - e.h
                                        e.vy = 0
                            elif e.vy < 0: # Rising
                                e.y = b.rect.bottom
                                e.vy = 0
                            e_rect = e.rect
                            
                # Check for falling off the map
                if e.y > SH:
                    e.alive = False
                    continue
                e.anim += dt * 5
            
            if abs(e.x - p.x) > 1000: continue
            
            if e.type == EType.PIRANHA and e.y >= GY - 48:
                continue
            
            if p.star and pr.colliderect(e.rect):
                e.dead = True; e.dead_t = 0.3
                self.kills += 1
                self.score += STOMP_S * 3
                if self._can_play_sound('stomp'):
                    SoundGenerator.stomp_sound(volume=self.master_volume * 0.5)
                for _ in range(18):
                    self.particles.append(Particle(
                        e.x+16, e.y+16,
                        random.uniform(-6,6), random.uniform(-10,-3),
                        random.uniform(0.4, 0.8), random.uniform(0.4, 0.8),
                        4, 4, 1,
                        (255, 200, 0), FIRE_ORANGE, 0.15
                    ))
                continue
            
            if pr.colliderect(e.rect):
                if p.vy > 0 and pr.bottom - e.rect.top < 22:
                    e.dead = True; e.dead_t = 0.3
                    p.vy = -9
                    self.kills += 1
                    
                    p.combo += 1
                    p.combo_timer = 2.5
                    p.max_combo = max(p.max_combo, p.combo)
                    
                    self.shake = 12
                    pygame.time.delay(35)
                    
                    if p.combo >= 5 and not self.fever_mode:
                        self.fever_mode = True
                        self.fever_t = 8.0
                        self._add_screen_effect("flash", 1.0, 0.4, (255, 0, 255))
                        self.shake = 20
                        if self._can_play_sound('checkpoint'):
                            SoundGenerator.checkpoint_sound(volume=self.master_volume * 0.7)
                    
                    combo_bonus = p.combo * COMBO_MULTIPLIER
                    stomp_val = (STOMP_S + combo_bonus) * (2 if self.fever_mode else 1)
                    self.score += stomp_val
                    
                    if self._can_play_sound('stomp'):
                        SoundGenerator.stomp_sound(volume=self.master_volume * 0.5)
                    if p.combo > 1 and self._can_play_sound('combo'):
                        SoundGenerator.combo_sound(p.combo, volume=self.master_volume * 0.4)
                    
                    popup_color = GOLD if p.combo > 1 else WHITE
                    self._add_score_popup(e.x, e.y, f"+{stomp_val}", 
                                         popup_color, p.combo > 3)
                    
                    for _ in range(10):
                        self.particles.append(Particle(
                            e.x+16, e.y+16,
                            random.uniform(-5,5), random.uniform(-8,-2),
                            random.uniform(0.3, 0.6), random.uniform(0.3, 0.6),
                            3, 3, 1,
                            GMBODY, GMHEAD, 0.2
                        ))
                
                else:
                    if p.inv <= 0 and not p.star:
                        if p.shield:
                            p.shield = False
                            p.shield_t = 0
                            p.inv = INV_T
                            p.power = PowerUp.NONE
                            self._add_score_popup(p.x, p.y, "SHIELD BROKEN!", RED, True)
                            self._add_screen_effect("flash", 0.6, 0.3, SHIELD_BLUE)
                            if self._can_play_sound('bump'):
                                SoundGenerator.bump_sound(volume=self.master_volume * 0.4)
                        elif p.big:
                            p.big = False; p.h = 48; p.y += 16
                            p.inv = INV_T; p.power = PowerUp.NONE
                            if self._can_play_sound('death', 0.3):
                                SoundGenerator.death_sound(volume=self.master_volume * 0.4)
                        else:
                            if self._can_play_sound('death', 0.5):
                                SoundGenerator.death_sound(volume=self.master_volume * 0.5)
                            self._die()
        
        for c in self.coins:
            if c.taken: continue
            if abs(c.x - p.x) > 500: continue
            
            dist = math.sqrt((c.x - p.x)**2 + (c.y - p.y)**2)
            if dist < 80:
                c.magnet_timer += dt
                if c.magnet_timer > 0.3:
                    angle = math.atan2(p.y - c.y, p.x - c.x)
                    c.x += math.cos(angle) * 5 * dt * 60
                    c.y += math.sin(angle) * 5 * dt * 60
            
            if pr.colliderect(c.rect):
                c.taken = True
                self.coins_c += 2 if self.fever_mode else 1
                self.score += COIN_S * (2 if self.fever_mode else 1)
                if self._can_play_sound('coin'):
                    SoundGenerator.coin_sound(volume=self.master_volume * 0.5)
                self._add_score_popup(c.x, c.y, f"+{COIN_S * (2 if self.fever_mode else 1)}", GOLD)
                
                for _ in range(5):
                    self.particles.append(Particle(
                        c.x, c.y,
                        random.uniform(-2,2), random.uniform(-4,-1),
                        0.3, 0.3, 2, 2, 0,
                        GOLD, GOLD, 0.03
                    ))
        
        if self.coins_c >= 100:
            self.coins_c -= 100
            if self.p: self.p.lives += 1
            self._add_score_popup(p.x, p.y, "1UP!", GREEN, True)
            if self._can_play_sound('powerup'):
                SoundGenerator.powerup_sound(volume=self.master_volume * 0.5)
        
        for m in self.mushrooms[:]:
            if m.taken: continue
            if m.spawn:
                m.spawn_t -= dt
                m.spawn = m.spawn_t > 0
                continue
            
            # Apply gravity to mushrooms
            m.vy += GRAV * dt * 60
            if m.vy > 12: m.vy = 12
            
            # 1. Horizontal movement and block collision
            m.x += m.vx * dt * 60
            m_rect = m.rect
            for b in self.blocks:
                if b.type in [BType.GROUND, BType.GRASS, BType.BRICK, BType.QUESTION, BType.PIPE]:
                    if abs(b.x - m.x) > 64: continue
                    if m_rect.colliderect(b.rect):
                        if m.vx > 0:
                            m.x = b.rect.left - 32
                            m.vx = -m.vx
                        elif m.vx < 0:
                            m.x = b.rect.right
                            m.vx = -m.vx
                        m_rect = m.rect
            
            # 2. Vertical movement and block collision
            m.y += m.vy * dt * 60
            m_rect = m.rect
            for b in self.blocks:
                if b.type in [BType.GROUND, BType.GRASS, BType.BRICK, BType.QUESTION, BType.PIPE]:
                    if abs(b.x - m.x) > 64: continue
                    if m_rect.colliderect(b.rect):
                        if m.vy > 0: # Falling
                            prev_y = m.y - m.vy * dt * 60
                            if prev_y + 32 <= b.rect.top + 4:
                                if b.rect.left < m.x + 32 - 6 and m.x + 6 < b.rect.right:
                                    m.y = b.rect.top - 32
                                    m.vy = 0
                        elif m.vy < 0: # Rising
                            m.y = b.rect.bottom
                            m.vy = 0
                        m_rect = m.rect
            
            # Fall out of world limit
            if m.y > SH:
                if m in self.mushrooms:
                    self.mushrooms.remove(m)
                continue
            
            m.anim += dt * 5
            
            if abs(m.x - p.x) > 500: continue
            
            if pr.colliderect(m.rect):
                m.taken = True; self.mushrooms.remove(m)
                
                if m.type == "super":
                    if not p.big:
                        p.big = True; p.h = 64; p.y -= 16
                        p.power = PowerUp.MUSHROOM
                    self.score += MUSH_SCORE * (2 if self.fever_mode else 1)
                elif m.type == "1up":
                    p.lives += 1
                elif m.type == "fire":
                    p.big = True; p.h = 64; p.y -= 16
                    p.power = PowerUp.FIRE
                    self.score += MUSH_SCORE * (2 if self.fever_mode else 1)
                    self._add_score_popup(m.x, m.y, "FIRE POWER!", (255, 100, 0), True)
                elif m.type == "shield":
                    p.shield = True; p.shield_t = 600
                    p.power = PowerUp.SHIELD
                    self.score += MUSH_SCORE * (2 if self.fever_mode else 1)
                    self._add_score_popup(m.x, m.y, "SHIELD!", SHIELD_BLUE, True)
                elif m.type == "speed":
                    p.speed_boost = True; p.speed_t = 600
                    p.power = PowerUp.SPEED
                    self.score += MUSH_SCORE * (2 if self.fever_mode else 1)
                    self._add_score_popup(m.x, m.y, "SPEED BOOST!", (255, 150, 0), True)
                
                if self._can_play_sound('powerup'):
                    SoundGenerator.powerup_sound(volume=self.master_volume * 0.5)
                self._add_score_popup(m.x, m.y, f"+{1000 * (2 if self.fever_mode else 1)}", GREEN)
        
        # Bouncing Fireball updates
        for fb in self.fireballs[:]:
            fb.life -= dt
            if not fb.alive:
                if fb in self.fireballs:
                    self.fireballs.remove(fb)
                continue
            
            fb.x += fb.vx * dt * 60
            fb.vy += GRAV * dt * 60
            if fb.vy > 15: fb.vy = 15
            fb.y += fb.vy * dt * 60
            
            if random.random() < 0.35:
                self.particles.append(Particle(
                    x=fb.x, y=fb.y,
                    vx=random.uniform(-1, 1), vy=random.uniform(-1, 1),
                    life=0.4, max_life=0.4,
                    size=random.randint(3, 5), start_size=random.randint(3, 5), end_size=1,
                    color=FIRE_ORANGE, end_color=(255, 230, 0),
                    gravity=0.02
                ))
            
            fb_rect = fb.rect
            hit = False
            
            if fb.reflected and fb_rect.colliderect(self.p.rect):
                hit = True
                self._damage_player()
            
            if not hit:
                for b in self.blocks:
                    if b.type in [BType.GROUND, BType.GRASS, BType.PIPE, BType.BRICK, BType.QUESTION]:
                        if abs(b.x - fb.x) > 64: continue
                        if fb_rect.colliderect(b.rect):
                            ot = fb_rect.bottom - b.rect.top
                            ob = b.rect.bottom - fb_rect.top
                            ol = fb_rect.right - b.rect.left
                            oR = b.rect.right - fb_rect.left
                            mo = min(ot, ob, ol, oR)
                            
                            if mo == ot and fb.vy >= 0:
                                fb.y = b.y - 8
                                fb.vy = -6.0
                                fb.bounces -= 1
                                if fb.bounces <= 0:
                                    hit = True
                            elif mo == ob and fb.vy < 0:
                                fb.y = b.y + b.h + 8
                                fb.vy = 2.0
                            elif mo in [ol, oR]:
                                hit = True
                            
            if hit:
                for _ in range(8):
                    self.particles.append(Particle(
                        x=fb.x, y=fb.y,
                        vx=random.uniform(-4, 4), vy=random.uniform(-4, 4),
                        life=0.3, max_life=0.3,
                        size=random.randint(2, 4), start_size=random.randint(2, 4), end_size=1,
                        color=(255, 100, 0), end_color=GOLD
                    ))
                self.fireballs.remove(fb)
                continue
            
            for e in self.enemies:
                if e.alive and not e.dead:
                    if fb_rect.colliderect(e.rect):
                        e.dead = True
                        e.dead_t = 0.3
                        self.kills += 1
                        
                        mult = 2 if self.fever_mode else 1
                        self.score += 200 * mult
                        self._add_score_popup(e.x, e.y, f"+{200 * mult}", (255, 100, 0))
                        
                        for _ in range(12):
                            self.particles.append(Particle(
                                x=e.x+16, y=e.y+16,
                                vx=random.uniform(-5, 5), vy=random.uniform(-8, -2),
                                life=0.5, max_life=0.5,
                                size=random.randint(3, 6), start_size=random.randint(3, 6), end_size=1,
                                color=(255, 50, 50), end_color=(255, 200, 0)
                            ))
                        
                        if self._can_play_sound('stomp'):
                            SoundGenerator.stomp_sound(volume=self.master_volume * 0.4)
                        
                        hit = True
                        break
            
            if hit and fb in self.fireballs:
                self.fireballs.remove(fb)
                
        # Boss Fight Triggering and Camera locking
        if p.x >= 16200 and not self.boss_triggered:
            self.boss_triggered = True
            self.boss = BowserBot(x=16500, y=-200)
            self._add_screen_effect("flash", 1.0, 0.6, WHITE)
            self.shake = 25
            if self._can_play_sound('checkpoint'):
                SoundGenerator.checkpoint_sound(volume=self.master_volume * 0.8)
            for y_idx in range(12):
                self.blocks.append(Block(15900, GY - TILE * y_idx, TILE, TILE, BType.BRICK))
                
        if self.boss_triggered and self.boss is not None:
            p.x = max(15900 + 16, min(p.x, 17200))
            self.cx = max(15900.0, min(self.cx, 16300.0))
            
        # BowserBot AI State Machine
        if self.boss is not None:
            boss = self.boss
            
            if boss.state == "descending":
                boss.y += 4 * dt * 60
                if boss.y >= GY - boss.h:
                    boss.y = GY - boss.h
                    boss.state = "active"
                    self.shake = 30
                    if self._can_play_sound('stomp'):
                        SoundGenerator.stomp_sound(volume=self.master_volume * 0.7)
            
            elif boss.state == "jumping":
                boss.vy += GRAV * dt * 60
                boss.x += boss.vx * dt * 60
                boss.y += boss.vy * dt * 60
                
                if boss.x < 15900 + 32:
                    boss.x = 15900 + 32
                    boss.vx *= -1
                elif boss.x > 17200 - boss.w - 32:
                    boss.x = 17200 - boss.w - 32
                    boss.vx *= -1
                    
                if boss.y >= GY - boss.h:
                    boss.y = GY - boss.h
                    boss.state = "active"
                    boss.vx = 0
                    boss.timer = 0
                    self.shake = 30
                    pygame.time.delay(45)
                    if self._can_play_sound('stomp'):
                        SoundGenerator.stomp_sound(volume=self.master_volume * 0.8)
                        
                    if not hasattr(self, 'boss_projectiles'):
                        self.boss_projectiles = []
                    self.boss_projectiles.append({
                        "x": boss.x, "y": GY - 24, "vx": -6.0, "w": 24, "h": 24, "type": "shockwave"
                    })
                    self.boss_projectiles.append({
                        "x": boss.x + boss.w - 24, "y": GY - 24, "vx": 6.0, "w": 24, "h": 24, "type": "shockwave"
                    })
            
            elif boss.state == "active":
                boss.anim += dt
                if boss.inv_t > 0: boss.inv_t -= dt
                if boss.shield_t > 0:
                    boss.shield_t -= dt
                    if boss.shield_t <= 0: boss.shielded = False
                
                if p.x < boss.x:
                    boss.vx = -1.5 if boss.phase == 1 else -2.5
                else:
                    boss.vx = 1.5 if boss.phase == 1 else 2.5
                
                if boss.health <= 1:
                    boss.vx *= 1.4
                    
                boss.x += boss.vx * dt * 60
                boss.x = max(15900 + 32, min(boss.x, 17200 - boss.w - 32))
                boss.timer += dt
                
                if boss.phase == 1:
                    if boss.timer >= 2.0:
                        boss.timer = 0.0
                        dx = p.x - (boss.x + boss.w//2)
                        dy = p.y - (boss.y + boss.h//2)
                        dist = max(1, math.sqrt(dx*dx + dy*dy))
                        proj_vx = (dx / dist) * 5.5
                        if not hasattr(self, 'boss_projectiles'):
                            self.boss_projectiles = []
                        self.boss_projectiles.append({
                            "x": boss.x + boss.w//2, "y": boss.y + boss.h//2,
                            "vx": proj_vx, "vy": -2.0, "w": 16, "h": 16, "type": "fireball"
                        })
                        if self._can_play_sound('bump'):
                            SoundGenerator.bump_sound(volume=self.master_volume * 0.4)
                
                elif boss.phase == 2:
                    if boss.timer >= 3.0:
                        boss.state = "jumping"
                        boss.vy = -15.0
                        boss.vx = 4.0 if p.x > boss.x else -4.0
                        boss.timer = 0.0
                        if self._can_play_sound('jump'):
                            SoundGenerator.jump_sound(volume=self.master_volume * 0.6)
                
                elif boss.phase == 3:
                    if not boss.shielded and boss.shield_t <= -4.0:
                        boss.shielded = True
                        boss.shield_t = 5.0
                        self._add_screen_effect("flash", 0.6, 0.4, (0, 255, 255))
                    
                    if boss.shielded:
                        if boss.timer >= 2.2:
                            boss.timer = 0.0
                            minion_type = random.choice([EType.GOOMBA, EType.KOOPA])
                            self.enemies.append(Enemy(
                                x=boss.x + boss.w//2, y=GY - 32,
                                w=32, h=32, type=minion_type,
                                vx=random.uniform(-2.5, 2.5)
                            ))
                            for _ in range(8):
                                self.particles.append(Particle(
                                    x=boss.x + boss.w//2, y=GY - 32,
                                    vx=random.uniform(-3, 3), vy=random.uniform(-6, -1),
                                    life=0.5, max_life=0.5,
                                    size=random.randint(3, 5), start_size=random.randint(3, 5), end_size=1,
                                    color=(0, 255, 255), end_color=(100, 150, 255)
                                ))
                    else:
                        boss.shield_t -= dt
                        if boss.timer >= 3.5:
                            boss.state = "jumping"
                            boss.vy = -14.0
                            boss.vx = 3.5 if p.x > boss.x else -3.5
                            boss.timer = 0.0
            
            elif boss.state == "dead":
                boss.timer -= dt
                boss.anim += dt * 10
                for _ in range(3):
                    self.particles.append(Particle(
                        x=boss.x + random.randint(0, boss.w),
                        y=boss.y + random.randint(0, boss.h),
                        vx=random.uniform(-5, 5), vy=random.uniform(-5, 5),
                        life=0.8, max_life=0.8,
                        size=random.randint(4, 8), start_size=random.randint(4, 8), end_size=1,
                        color=(0, 255, 255), end_color=(150, 50, 255)
                    ))
                if boss.timer <= 0:
                    self.boss = None
                    self.shake = 40
                    self._add_screen_effect("flash", 1.0, 0.8, GOLD)
                    self.blocks = [b for b in self.blocks if not (b.x == 15900)]
                    self._add_score_popup(boss.x + boss.w//2, boss.y + boss.h//2, "VICTORY!", GOLD, True)
                    self.score += 10000
                    if self._can_play_sound('powerup'):
                        SoundGenerator.powerup_sound(volume=self.master_volume * 0.8)
            
            # Fireball-Boss collisions
            if boss.state != "dead":
                for fb in self.fireballs[:]:
                    if fb.rect.colliderect(boss.rect):
                        if fb.reflected: continue
                        if boss.shielded:
                            fb.vx = -fb.vx * 1.2
                            fb.vy = random.uniform(-5, -2)
                            fb.reflected = True
                            if self._can_play_sound('bump'):
                                SoundGenerator.bump_sound(volume=self.master_volume * 0.4)
                            for _ in range(8):
                                self.particles.append(Particle(
                                    x=fb.x, y=fb.y,
                                    vx=random.uniform(-4, 4), vy=random.uniform(-4, 4),
                                    life=0.3, max_life=0.3,
                                    size=random.randint(2, 4), start_size=random.randint(2, 4), end_size=1,
                                    color=(0, 255, 255)
                                ))
                        else:
                            self.fireballs.remove(fb)
                            for _ in range(8):
                                self.particles.append(Particle(
                                    x=fb.x, y=fb.y,
                                    vx=random.uniform(-4, 4), vy=random.uniform(-4, 4),
                                    life=0.3, max_life=0.3,
                                    size=random.randint(2, 4), start_size=random.randint(2, 4), end_size=1,
                                    color=(255, 100, 0)
                                ))
                            if boss.inv_t <= 0:
                                boss.health -= 1
                                boss.inv_t = 1.5
                                self.shake = 15
                                pygame.time.delay(35)
                                self._add_score_popup(boss.x + boss.w//2, boss.y, "HIT!", GOLD, True)
                                
                                if 6 <= boss.health <= 10:
                                    boss.phase = 2
                                elif boss.health <= 5:
                                    boss.phase = 3
                                    
                                if boss.health <= 0:
                                    boss.state = "dead"
                                    boss.timer = 2.5
                                    if self._can_play_sound('gameover'):
                                        SoundGenerator.gameover_sound(volume=self.master_volume * 0.8)
                                else:
                                    if self._can_play_sound('bump'):
                                        SoundGenerator.bump_sound(volume=self.master_volume * 0.5)
                                    
            # Stomp check on Bowser-Bot
            if boss.state != "dead":
                if pr.colliderect(boss.rect):
                    if p.vy > 0 and pr.bottom - boss.rect.top < 25:
                        if boss.shielded:
                            p.vy = -8.0
                            if self._can_play_sound('bump'):
                                SoundGenerator.bump_sound(volume=self.master_volume * 0.3)
                        elif boss.inv_t <= 0:
                            boss.health -= 1
                            boss.inv_t = 1.5
                            p.vy = -12.0
                            self.shake = 22
                            pygame.time.delay(45)
                            self._add_score_popup(boss.x + boss.w//2, boss.y, "CRITICAL!", GOLD, True)
                            
                            if 6 <= boss.health <= 10:
                                boss.phase = 2
                            elif boss.health <= 5:
                                boss.phase = 3
                                
                            if boss.health <= 0:
                                boss.state = "dead"
                                boss.timer = 2.5
                                if self._can_play_sound('gameover'):
                                    SoundGenerator.gameover_sound(volume=self.master_volume * 0.8)
                            else:
                                if self._can_play_sound('stomp'):
                                    SoundGenerator.stomp_sound(volume=self.master_volume * 0.6)
                        else:
                            p.vy = -7.0
                    else:
                        if p.inv <= 0 and not p.star:
                            if p.shield:
                                p.shield = False
                                p.shield_t = 0
                                p.inv = INV_T
                                self._add_score_popup(p.x, p.y, "SHIELD BROKEN!", RED, True)
                                self._add_screen_effect("flash", 0.6, 0.3, SHIELD_BLUE)
                                if self._can_play_sound('bump'):
                                    SoundGenerator.bump_sound(volume=self.master_volume * 0.4)
                            elif p.big:
                                p.big = False
                                p.h = 48
                                p.y += 16
                                p.inv = INV_T
                                p.power = PowerUp.NONE
                                if self._can_play_sound('death', 0.3):
                                    SoundGenerator.death_sound(volume=self.master_volume * 0.4)
                            else:
                                if self._can_play_sound('death', 0.5):
                                    SoundGenerator.death_sound(volume=self.master_volume * 0.5)
                                self._die()
                                
        # Update boss projectiles
        if hasattr(self, 'boss_projectiles'):
            for bp in self.boss_projectiles[:]:
                bp["x"] += bp["vx"] * dt * 60
                if "vy" in bp:
                    bp["vy"] += GRAV * dt * 60
                    bp["y"] += bp["vy"] * dt * 60
                
                if bp["x"] < 15900 or bp["x"] > 17500 or bp["y"] > GY + 50:
                    self.boss_projectiles.remove(bp)
                    continue
                
                bp_rect = pygame.Rect(int(bp["x"]), int(bp["y"]), bp["w"], bp["h"])
                if bp_rect.colliderect(p.rect):
                    self.boss_projectiles.remove(bp)
                    if p.star: continue
                    
                    if p.inv <= 0:
                        if p.shield:
                            p.shield = False
                            p.shield_t = 0
                            p.inv = INV_T
                            self._add_score_popup(p.x, p.y, "SHIELD BROKEN!", RED, True)
                            self._add_screen_effect("flash", 0.6, 0.3, SHIELD_BLUE)
                            if self._can_play_sound('bump'):
                                SoundGenerator.bump_sound(volume=self.master_volume * 0.4)
                        elif p.big:
                            p.big = False
                            p.h = 48
                            p.y += 16
                            p.inv = INV_T
                            p.power = PowerUp.NONE
                            if self._can_play_sound('death', 0.3):
                                SoundGenerator.death_sound(volume=self.master_volume * 0.4)
                        else:
                            if self._can_play_sound('death', 0.5):
                                SoundGenerator.death_sound(volume=self.master_volume * 0.5)
                            self._die()
                            
        # Fever Mode updates
        if self.fever_mode:
            self.fever_t -= dt
            if random.random() < 0.4 and self.p:
                import colorsys
                hue = (time.time() * 200) % 360
                r_col, g_col, b_col = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
                self.particles.append(Particle(
                    x=self.p.x + random.randint(0, self.p.w),
                    y=self.p.y + random.randint(0, self.p.h),
                    vx=random.uniform(-2, 2), vy=random.uniform(-4, -1),
                    life=0.6, max_life=0.6,
                    size=random.randint(3, 6), start_size=random.randint(3, 6), end_size=1,
                    color=(int(r_col*255), int(g_col*255), int(b_col*255)),
                    end_color=(255, 255, 255)
                ))
            if self.fever_t <= 0:
                self.fever_mode = False
                self.fever_t = 0.0
        
        for pt in self.particles[:]:
            pt.update(dt)
            if not pt.alive: self.particles.remove(pt)
        
        for sp in self.score_popups[:]:
            sp.update(dt)
            if not sp.alive: self.score_popups.remove(sp)
        
        for se in self.screen_effects[:]:
            se.update(dt)
            if not se.alive: self.screen_effects.remove(se)
        
        if self.shake > 0:
            self.shake *= 0.85
            if self.shake < 0.05: self.shake = 0
            self.sx = random.uniform(-self.shake, self.shake)
            self.sy = random.uniform(-self.shake*0.5, self.shake*0.3)
        else:
            self.sx = 0; self.sy = 0
        
        if self.flag_reached:
            self.flag_timer -= dt
            p.vx *= 0.9
            if self.flag_timer <= 0:
                self.state = State.WIN
        
        self.gt = time.time() - self.st
        if self.gt > LVL_TIME:
            self._die()
        
        if self.slow_mo < 1.0:
            self.slow_mo = min(1.0, self.slow_mo + dt * 0.5)
    
    def _damage_player(self):
        p = self.p
        if p is None or p.inv > 0 or p.star: return
        if p.shield:
            p.shield = False
            p.shield_t = 0
            p.inv = INV_T
            p.power = PowerUp.NONE
            self._add_score_popup(p.x, p.y, "SHIELD BROKEN!", RED, True)
            self._add_screen_effect("flash", 0.6, 0.3, SHIELD_BLUE)
            if self._can_play_sound('bump'):
                SoundGenerator.bump_sound(volume=self.master_volume * 0.4)
        elif p.big:
            p.big = False; p.h = 48; p.y += 16
            p.inv = INV_T; p.power = PowerUp.NONE
            if self._can_play_sound('death', 0.3):
                SoundGenerator.death_sound(volume=self.master_volume * 0.4)
        else:
            if self._can_play_sound('death', 0.5):
                SoundGenerator.death_sound(volume=self.master_volume * 0.5)
            self._die()

    def _die(self):
        if self.p is None: return
        self.p.lives -= 1
        self.shake = 10
        
        if self.p.lives <= 0:
            self.state = State.OVER
            self.lives = 0
            if self._can_play_sound('gameover', 1.0):
                SoundGenerator.gameover_sound(volume=self.master_volume * 0.5)
            if self.score > self.hs:
                self.hs = self.score
            if self.p.max_combo > self.max_combo_record:
                self.max_combo_record = self.p.max_combo
            try:
                with open(SCORE_F, 'w') as f:
                    json.dump({
                        'hs': self.hs,
                        'max_combo': self.max_combo_record,
                        'date': time.strftime('%Y-%m-%d %H:%M:%S')
                    }, f)
            except: pass
        else:
            start_x = 100
            if self.last_checkpoint:
                start_x = self.last_checkpoint.x
            
            self.p.x = start_x
            self.p.y = GY - 48
            self.p.vx = self.p.vy = 0
            self.p.ground = True
            self.p.was_on_ground = True
            self.p.jumps = self.p.max_jumps
            self.p.inv = INV_T
            self.p.big = False
            self.p.star = False
            self.p.shield = False
            self.p.speed_boost = False
            self.p.power = PowerUp.NONE
            self.p.h = 48
            self.p.combo = 0
            self.p.combo_timer = 0
            self.slow_mo = 0.3
    
    def _draw_gradient_sky(self, top_color, bottom_color):
        key = (top_color, bottom_color)
        if not hasattr(self, '_sky_cache'):
            self._sky_cache = {}
        if key not in self._sky_cache:
            surf = pygame.Surface((2, SH))
            for y in range(SH):
                ratio = y / SH
                r = int(top_color[0] * (1-ratio) + bottom_color[0] * ratio)
                g = int(top_color[1] * (1-ratio) + bottom_color[1] * ratio)
                b = int(top_color[2] * (1-ratio) + bottom_color[2] * ratio)
                pygame.draw.line(surf, (r, g, b), (0, y), (1, y))
            self._sky_cache[key] = pygame.transform.scale(surf, (SW, SH))
        self.s.blit(self._sky_cache[key], (0, 0))

    def _render_background(self):
        if self.fever_mode:
            pulse = (math.sin(time.time() * 8) + 1.0) * 0.5
            r1 = int(20 + 30 * pulse)
            g1 = int(5 + 5 * pulse)
            b1 = int(50 + 50 * pulse)
            r2 = int(80 + 40 * pulse)
            g2 = int(10 + 10 * pulse)
            b2 = int(150 + 50 * pulse)
            self._draw_gradient_sky((r1, g1, b1), (r2, g2, b2))
        elif self.weather == Weather.NIGHT:
            self._draw_gradient_sky((10, 10, 40), (20, 30, 60))
        else:
            # Custom themes based on level to introduce different worlds
            if self.level == 1:
                # Classic World: Bright blue sky
                self._draw_gradient_sky(SKY_TOP, SKY_BOTTOM)
            elif self.level == 2:
                # Underworld Cave World: Deep purple/magenta cave tones
                self._draw_gradient_sky((15, 10, 25), (45, 20, 60))
            elif self.level == 3:
                # Sunset Volcano World: Vivid red, orange, and purple skies
                self._draw_gradient_sky((120, 15, 40), (230, 95, 20))
            elif self.level == 4:
                # Ice Mountain World: Frosty cyan/blue gradients
                self._draw_gradient_sky((10, 80, 130), (170, 220, 240))
            else:
                # Cosmic Space World: pitch dark void
                self._draw_gradient_sky((0, 0, 8), (10, 10, 25))
        
        if self.weather == Weather.NIGHT:
            if not hasattr(self, '_star_surface_cache'):
                self._star_surface_cache = {}
            for sx, sy, size, twinkle in self.stars:
                alpha = int(128 + 127 * math.sin(time.time() * twinkle))
                alpha_q = (alpha // 15) * 15
                key = (size, alpha_q)
                if key not in self._star_surface_cache:
                    star_surf = pygame.Surface((int(size*3), int(size*3)), pygame.SRCALPHA)
                    pygame.draw.circle(star_surf, (255, 255, 200, alpha_q), 
                                     (int(size*1.5), int(size*1.5)), int(size))
                    self._star_surface_cache[key] = star_surf
                self.s.blit(self._star_surface_cache[key], (sx, sy))
        
        for mx, my, mw, mh in self.mountains:
            sx = mx - self.cx * 0.1 + self.sx
            if -300 <= sx <= SW + 300:
                color = MOUNTAIN_FAR if self.weather != Weather.NIGHT else (60, 60, 80)
                pygame.draw.polygon(self.s, color,
                    [(sx, my+mh), (sx+mw//2, my), (sx+mw, my+mh)])
        
        for hx, hy, hw, hh in self.hills_far:
            sx = hx - self.cx * 0.3 + self.sx
            if -200 <= sx <= SW + 200:
                color = HILL_FAR if self.weather != Weather.NIGHT else (40, 80, 40)
                pygame.draw.ellipse(self.s, color, (sx, hy, hw, hh))
        
        for hx, hy, hw, hh in self.hills_near:
            sx = hx - self.cx * 0.5 + self.sx
            if -150 <= sx <= SW + 150:
                color = HILL_NEAR if self.weather != Weather.NIGHT else (0, 100, 0)
                pygame.draw.ellipse(self.s, color, (sx, hy, hw, hh))
        
        for cx, cy, cw, cs in self.clouds:
            bx = (cx - self.cx * cs) % (SW + 300) - 150
            ch = cw // 3
            cloud_color = CLOUD_COLOR if self.weather != Weather.NIGHT else (100, 100, 120)
            cloud_shadow = CLOUD_SHADOW if self.weather != Weather.NIGHT else (70, 70, 90)
            
            for dx, dy, dw, dh in [(0, ch//2, cw, ch), (cw//4, 0, cw//2, ch)]:
                pygame.draw.ellipse(self.s, cloud_shadow, (bx+dx+2, cy+dy+2, dw, dh))
                pygame.draw.ellipse(self.s, cloud_color, (bx+dx, cy+dy, dw, dh))
    
    def _render_weather_effects(self):
        if self.weather == Weather.RAIN:
            for _ in range(30):
                rx = random.randint(0, SW)
                ry = random.randint(0, SH)
                pygame.draw.line(self.s, (150, 180, 255, 100), 
                               (rx, ry), (rx-2, ry+8), 1)
        elif self.weather == Weather.SNOW:
            for _ in range(20):
                sx = random.randint(0, SW)
                sy = random.randint(0, SH)
                pygame.draw.circle(self.s, (255, 255, 255, 150), (sx, sy), 2)
    
    def _render(self):
        self._render_background()
        

        
        for cp in self.checkpoints:
            sx = cp.x - self.cx + self.sx
            if -64 <= sx <= SW + 64:
                draw_checkpoint(self.s, int(sx), GY-32, cp.activated)
        
        for b in self.blocks:
            bx, by = b.x - self.cx + self.sx, b.y + self.sy
            by += b.bounce if b.bounce > 0 else 0
            
            if bx < -64 or bx > SW + 64: continue
            
            # Determine tile colors based on level themes
            theme_colors = {
                1: { # Classic World
                    "grass": (0, 168, 0), "grass_l": (56, 208, 56),
                    "ground": (184, 104, 32), "ground_d": (152, 88, 24)
                },
                2: { # Underworld Cave World
                    "grass": (40, 20, 60), "grass_l": (80, 40, 120),
                    "ground": (40, 40, 50), "ground_d": (20, 20, 30)
                },
                3: { # Sunset Volcano World
                    "grass": (220, 40, 10), "grass_l": (255, 100, 30),
                    "ground": (70, 15, 10), "ground_d": (40, 5, 0)
                },
                4: { # Ice Mountain World
                    "grass": (80, 180, 220), "grass_l": (160, 230, 255),
                    "ground": (120, 150, 180), "ground_d": (80, 110, 140)
                }
            }
            # Fallback theme for level 5+ (Space World)
            active_theme = theme_colors.get(self.level, {
                "grass": (10, 10, 30), "grass_l": (0, 180, 255),
                "ground": (15, 15, 20), "ground_d": (5, 5, 10)
            })

            if b.type == BType.GRASS:
                pygame.draw.rect(self.s, active_theme["grass"], (bx, by, 32, 32))
                pygame.draw.rect(self.s, active_theme["grass_l"], (bx, by, 32, 6))
            elif b.type == BType.GROUND:
                pygame.draw.rect(self.s, active_theme["ground"], (bx, by, 32, 32))
                pygame.draw.rect(self.s, active_theme["ground_d"], (bx+4, by+4, 8, 8))
            elif b.type == BType.BRICK:
                draw_brick(self.s, bx, by, b.bounce)
            elif b.type == BType.QUESTION:
                draw_qblock(self.s, bx, by, b.used, b.bounce)
            elif b.type == BType.HIDDEN:
                if b.hidden:
                    draw_brick(self.s, bx, by, b.bounce)
            elif b.type == BType.PIPE:
                draw_pipe(self.s, bx, by, b.w, b.h)
            elif b.type == BType.FLAG:
                draw_flag(self.s, bx, by)
        
        for c in self.coins:
            if c.taken: continue
            sx = c.x - self.cx + self.sx
            if -32 <= sx <= SW + 32:
                draw_coin(self.s, int(sx+8), 
                         int(c.y+8+math.sin(time.time()*3+c.off)*3), c.off)
        
        for m in self.mushrooms:
            if m.taken: continue
            sx = m.x - self.cx + self.sx
            sy = m.y
            if m.spawn:
                sy = GY - 64 + int((0.5 - m.spawn_t) * 64)
            if -64 <= sx <= SW + 64:
                draw_mushroom(self.s, sx, sy+int(math.sin(m.anim*3)*2), 0, m.type)
                
        # Draw BowserBot if active
        if self.boss is not None:
            boss_sx = self.boss.x - self.cx + self.sx
            if -128 <= boss_sx <= SW + 128:
                draw_shadow(self.s, boss_sx + self.boss.w//2, GY, self.boss.w + 16, 80)
                draw_bowser(self.s, boss_sx, self.boss.y + self.sy, self.boss.w, self.boss.h,
                            shielded=self.boss.shielded, inv_t=self.boss.inv_t, anim=self.boss.anim)
                            
        # Draw active fireballs
        for fb in self.fireballs:
            if not fb.alive: continue
            sx = fb.x - self.cx + self.sx
            if -32 <= sx <= SW + 32:
                pygame.draw.circle(self.s, FIRE_ORANGE, (int(sx), int(fb.y + self.sy)), 8)
                pygame.draw.circle(self.s, GOLD, (int(sx), int(fb.y + self.sy)), 5)
                pygame.draw.circle(self.s, WHITE, (int(sx), int(fb.y + self.sy)), 2)
                
        # Draw boss projectiles
        if hasattr(self, 'boss_projectiles'):
            for bp in self.boss_projectiles:
                sx = bp["x"] - self.cx + self.sx
                if -64 <= sx <= SW + 64:
                    if bp.get("type") == "shockwave":
                        pygame.draw.rect(self.s, (0, 255, 255), (sx, bp["y"] + self.sy, bp["w"], bp["h"]), 2)
                        pygame.draw.rect(self.s, (0, 150, 255), (sx + 3, bp["y"] + self.sy + 3, bp["w"] - 6, bp["h"] - 6))
                    else:
                        pygame.draw.circle(self.s, (255, 0, 100), (int(sx), int(bp["y"] + self.sy)), 12)
                        pygame.draw.circle(self.s, (255, 100, 200), (int(sx), int(bp["y"] + self.sy)), 8)
                        pygame.draw.circle(self.s, WHITE, (int(sx), int(bp["y"] + self.sy)), 4)
        
        for e in self.enemies:
            if not e.alive: continue
            sx, sy = e.x - self.cx + self.sx, e.y + self.sy
            if -64 <= sx <= SW + 64:
                bob = math.sin(e.anim) * 2
                
                # Draw high-fidelity squish and fade-out for dead enemies
                if e.dead:
                    progress = max(0.0, min(1.0, e.dead_t / 0.3))
                    squish_h = max(2, int(32 * progress))
                    alpha = max(0, min(255, int(255 * progress)))
                    
                    cached_surf = None
                    if e.type == EType.GOOMBA:
                        cached_surf = _goomba_cache.get(round(bob, 1))
                    elif e.type == EType.KOOPA:
                        cached_surf = _koopa_cache.get(round(bob, 1))
                    elif e.type == EType.PIRANHA:
                        cached_surf = _piranha_cache.get('base')
                        
                    draw_shadow(self.s, sx+16, sy+32, int(24 * progress), int(40 * progress))
                    
                    if cached_surf is not None:
                        scaled_surf = pygame.transform.scale(cached_surf, (32, squish_h))
                        scaled_surf.set_alpha(alpha)
                        if e.type == EType.PIRANHA:
                            old_clip = self.s.get_clip()
                            self.s.set_clip(pygame.Rect(0, 0, SW, int(GY - 64 + self.sy)))
                            self.s.blit(scaled_surf, (sx, sy + (32 - squish_h)))
                            self.s.set_clip(old_clip)
                        else:
                            self.s.blit(scaled_surf, (sx, sy + (32 - squish_h)))
                else:
                    draw_shadow(self.s, sx+16, sy+32, 24, 40)
                    if e.type == EType.GOOMBA:
                        draw_goomba(self.s, sx, sy, bob)
                    elif e.type == EType.KOOPA:
                        draw_koopa(self.s, sx, sy, bob)
                    elif e.type == EType.PIRANHA:
                        old_clip = self.s.get_clip()
                        self.s.set_clip(pygame.Rect(0, 0, SW, int(GY - 64 + self.sy)))
                        draw_piranha(self.s, sx, sy, bob)
                        self.s.set_clip(old_clip)
        
        for pt in self.particles:
            sx = pt.x - self.cx + self.sx
            if -64 <= sx <= SW + 64 and pt.alive:
                try:
                    color = pt.get_color()
                    if len(color) >= 4 and color[3] > 0:
                        pt_surf = pygame.Surface((pt.size*2, pt.size*2), pygame.SRCALPHA)
                        if pt.shape == "circle":
                            pygame.draw.circle(pt_surf, color, (pt.size, pt.size), pt.size)
                        else:
                            pygame.draw.rect(pt_surf, color, (0, 0, pt.size*2, pt.size*2))
                        
                        if getattr(pt, 'angle', 0.0) != 0.0:
                            rotated_surf = pygame.transform.rotate(pt_surf, pt.angle)
                            new_rect = rotated_surf.get_rect(center=(int(sx), int(pt.y + self.sy)))
                            self.s.blit(rotated_surf, new_rect.topleft)
                        else:
                            self.s.blit(pt_surf, (sx - pt.size, pt.y + self.sy - pt.size))
                except:
                    pass
        
        if self.p is not None:
            trail_list = list(self.p.trail)
            for i, (tx, ty, tt) in enumerate(trail_list):
                alpha = int(80 * (i / max(1, len(trail_list))) * (1 - (time.time() - tt) / 0.15))
                if alpha > 0:
                    sx = tx - self.cx + self.sx
                    trail_surf = pygame.Surface((self.p.w, self.p.h), pygame.SRCALPHA)
                    if self.fever_mode:
                        import colorsys
                        hue = (i * 15 + int(time.time() * 360)) % 360
                        r_col, g_col, b_col = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
                        color = (int(r_col * 255), int(g_col * 255), int(b_col * 255))
                    elif self.p.star:
                        color = GOLD
                    elif self.p.speed_boost:
                        color = (255, 100, 255) if (i % 2 == 0) else (0, 220, 255)
                    else:
                        color = MRED
                    pygame.draw.rect(trail_surf, (*color, alpha), (0, 0, self.p.w, self.p.h))
                    self.s.blit(trail_surf, (sx - self.p.w//2, ty + self.sy - self.p.h//2))
        
        if self.p is not None:
            sx, sy = self.p.x - self.cx + self.sx, self.p.y + self.sy
            if -96 <= sx <= SW + 96:
                if abs(self.p.vx) > 0.3 and self.p.ground:
                    self.p.anim += abs(self.p.vx) * 0.06
                
                if self.p.ground:
                    draw_shadow(self.s, sx + self.p.w//2, GY, self.p.w + 8, 60)
                
                draw_mario(self.s, int(sx), int(sy), self.p.w, self.p.h,
                          self.p.dir, self.p.anim, self.p.ground,
                          self.p.star, self.p.inv, self.p.power, self.p.ducking)
                
                if self.p.shield:
                    shield_radius = max(self.p.w, self.p.h) // 2 + 10
                    shield_center = (int(sx) + self.p.w // 2, int(sy) + self.p.h // 2)
                    shield_surf = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
                    pulse = math.sin(time.time() * 12) * 20
                    alpha = int(120 + pulse)
                    pygame.draw.circle(shield_surf, (200, 220, 255, alpha + 60), (shield_radius, shield_radius), shield_radius, 2)
                    pygame.draw.circle(shield_surf, (100, 150, 255, alpha // 2), (shield_radius, shield_radius), shield_radius - 2)
                    self.s.blit(shield_surf, (shield_center[0] - shield_radius, shield_center[1] - shield_radius))
        
        for sp in self.score_popups:
            sx = sp.x - self.cx + self.sx
            if -150 <= sx <= SW + 150 and sp.alive:
                alpha = max(0, min(255, int(255 * sp.life / sp.max_life)))
                try:
                    txt = self.fm.render(sp.text, True, sp.color[:3])
                    if sp.pulse:
                        scaled_size = int(txt.get_width() * sp.scale), int(txt.get_height() * sp.scale)
                        txt = pygame.transform.scale(txt, scaled_size)
                    txt.set_alpha(alpha)
                    self.s.blit(txt, (sx - txt.get_width()//2, sp.y + self.sy))
                except:
                    pass
        
        if self.p is not None and self.p.combo > 1 and self.p.combo_timer > 0:
            combo_text = f"COMBO x{self.p.combo}!"
            combo_color = GOLD if self.p.combo >= 5 else WHITE
            combo_txt = self.fb.render(combo_text, True, combo_color)
            combo_rect = combo_txt.get_rect(center=(SW//2, SH//2 - 60))
            
            pulse = math.sin(time.time() * 8) * 0.05
            scale = 1 + pulse
            scaled_w = int(combo_rect.w * scale)
            scaled_h = int(combo_rect.h * scale)
            scaled_txt = pygame.transform.scale(combo_txt, (scaled_w, scaled_h))
            self.s.blit(scaled_txt, scaled_txt.get_rect(center=(SW//2, SH//2 - 60)))
        
        self._render_weather_effects()
        self._hud()
        self._camera()
        
        if self.state == State.MENU: self._menu()
        elif self.state == State.PAUSE: self._pause()
        elif self.state == State.OVER: self._gameover()
        elif self.state == State.CONTROLS: self._controls_screen()
        elif self.state == State.WIN: self._win_screen()
        elif self.state == State.SETTINGS: self._settings_screen()
        
        for se in self.screen_effects:
            if se.type == "flash" and se.alive:
                alpha = se.get_alpha()
                self.flash_overlay.fill(se.color)
                self.flash_overlay.set_alpha(alpha // 3)
                self.s.blit(self.flash_overlay, (0, 0))
        
        self.s.blit(self.vignette_surf, (0, 0))
        
        if self.transition_alpha > 0:
            self.black_overlay.set_alpha(min(255, int(self.transition_alpha)))
            self.s.blit(self.black_overlay, (0, 0))
            self.transition_alpha += self.transition_dir * 8
            if self.transition_alpha > 255:
                self.transition_alpha = 255
                self.transition_dir = -1
            elif self.transition_alpha < 0:
                self.transition_alpha = 0
                self.transition_dir = 0
        
        if self.show_fps:
            fps_txt = self.ft.render(f"FPS: {int(self.clock.get_fps())}", True, GREEN)
            self.s.blit(fps_txt, (SW - 100, SH - 25))
        
        pygame.display.flip()
    
    def _hud(self):
        # Draw a premium, dark-tinted retro header panel
        pygame.draw.rect(self.s, (12, 12, 20, 240), (0, 0, SW, 52))
        
        # Draw golden layered trim at the bottom of the HUD
        pygame.draw.rect(self.s, GOLD, (0, 48, SW, 4))
        pygame.draw.rect(self.s, (150, 110, 0), (0, 50, SW, 2))
        
        # 1. MARIO Column
        draw_pixel_star(self.s, 24, 16, 3)
        draw_retro_text(self.s, "MARIO", self.fs, 60, 4)
        draw_retro_text(self.s, f"{self.score:06d}", self.fs, 60, 26)
        
        # 2. COINS Column
        draw_coin(self.s, 345, 24, 0)
        draw_retro_text(self.s, "COINS", self.fs, 380, 4)
        draw_retro_text(self.s, f"x{self.coins_c % 100:02d}", self.fs, 380, 26, GOLD)
        
        # 3. WORLD Column
        pygame.draw.rect(self.s, WHITE, (535, 12, 2, 28))
        pygame.draw.polygon(self.s, RED, [(537, 12), (549, 18), (547, 24)])
        draw_retro_text(self.s, "WORLD", self.fs, 565, 4)
        draw_retro_text(self.s, f"1-{self.level}", self.fs, 580, 26)

        # 3.5 World Map Sembolleri / Progress Bar
        map_x, map_y = 650, 16
        # Draw small background track line
        pygame.draw.line(self.s, (80, 80, 80), (map_x, map_y + 10), (map_x + 220, map_y + 10), 4)
        
        # Draw 5 map indicators corresponding to the 5 worlds
        world_symbols = ["🟢", "🟣", "🔴", "❄️", "⭐"]
        world_names = ["Klasik", "Magara", "Volkan", "Buz", "Uzay"]
        for idx in range(5):
            wx = map_x + idx * 48
            is_passed = self.level > idx + 1
            is_current = self.level == idx + 1
            
            # Indicator color
            if is_current:
                color = GOLD
                # Pulse outline for active world
                pulse_s = int(8 + math.sin(time.time() * 6) * 3)
                pygame.draw.circle(self.s, GOLD, (wx + 10, map_y + 10), pulse_s, 2)
            elif is_passed:
                color = GREEN
            else:
                color = GRAY
                
            # Render symbol
            sym_txt = self.ft.render(world_symbols[idx], True, WHITE)
            self.s.blit(sym_txt, (wx, map_y - 2))
            
            # Tiny level number label below
            lbl_color = GOLD if is_current else (LIGHT_GRAY if is_passed else DARK_GRAY)
            tiny_lbl = self.ft.render(f"W{idx+1}", True, lbl_color)
            self.s.blit(tiny_lbl, (wx - 2, map_y + 16))
        
        # 4. TIME Column
        draw_pixel_clock(self.s, 925, 16, 3)
        draw_retro_text(self.s, "TIME", self.fs, 960, 4)
        tl = max(0, LVL_TIME - self.gt)
        time_color = RED if tl < 60 else WHITE
        draw_retro_text(self.s, f"{int(tl):03d}", self.fs, 970, 26, time_color)
        
        # 5. LIVES Column
        draw_pixel_heart(self.s, 1105, 16, 3)
        draw_retro_text(self.s, "LIVES", self.fs, 1140, 4)
        lives_val = max(0, self.p.lives if self.p else 0)
        draw_retro_text(self.s, f"x{lives_val}", self.fs, 1155, 26)
        
        if self.boss is not None and self.boss.state != "dead":
            b_health_x = SW - 320
            b_health_y = 65
            b_health_w = 300
            b_health_h = 16
            
            draw_retro_text(self.s, "BOSS: BOWSER-BOT", self.fs, b_health_x, b_health_y - 24, (255, 0, 100))
            
            # Retro pixel-art style border for Boss Health Bar
            pygame.draw.rect(self.s, BLACK, (b_health_x, b_health_y, b_health_w, b_health_h))
            pygame.draw.rect(self.s, WHITE, (b_health_x, b_health_y, b_health_w, b_health_h), 2)
            
            ratio = max(0.0, min(1.0, self.boss.health / self.boss.max_health))
            if ratio > 0:
                filled_w = int((b_health_w - 6) * ratio)
                pygame.draw.rect(self.s, (255, 0, 0), (b_health_x + 3, b_health_y + 3, filled_w, b_health_h - 6))
                
        # Draw Fever Mode banner
        if self.fever_mode:
            fever_val = max(0.0, self.fever_t)
            colors = [(255, 0, 255), (0, 255, 255), (255, 255, 0)]
            color_idx = int(time.time() * 15) % len(colors)
            draw_retro_text(self.s, f"FEVER MODE 2X: {fever_val:.1f}s", self.fs, 15, 65, colors[color_idx])
    
    def _camera(self):
        if self.control_mode == 0 or self.hand is None: return
        frame = self.hand.get_frame()
        if frame is None: return
        try:
            f = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (180, 135))
            sf = pygame.surfarray.make_surface(f.swapaxes(0, 1))
            px, py = SW - 195, SH - 150
            
            # Premium retro camera panel container
            pygame.draw.rect(self.s, BLACK, (px-3, py-3, 186, 141))
            pygame.draw.rect(self.s, WHITE, (px-3, py-3, 186, 141), 2)
            self.s.blit(sf, (px, py))
            
            # Draw subtle blue crosshair grid showing steering center
            pygame.draw.line(self.s, (0, 120, 255, 128), (px, py + 135//2), (px + 180, py + 135//2), 1)
            pygame.draw.line(self.s, (0, 120, 255, 128), (px + 180//2, py), (px + 180//2, py + 135), 1)
            
            # Draw active hand steering target position crosshair
            hx = int(self.hand.sx * 180)
            hy = int(self.hand.sy * 135)
            if 0 <= hx <= 180 and 0 <= hy <= 135:
                pygame.draw.circle(self.s, (0, 255, 255), (px + hx, py + hy), 6, 1)
                pygame.draw.circle(self.s, (0, 255, 255), (px + hx, py + hy), 2)
                
            # Draw label
            lbl = self.ft.render("EL TAKIBI", True, GOLD)
            lbl_bg = pygame.Surface((lbl.get_width()+6, 20))
            lbl_bg.fill(BLACK)
            self.s.blit(lbl_bg, (px+2, py-22))
            self.s.blit(lbl, (px+5, py-21))
            
            # Gesture Indicators
            gest_y = py + 145
            if self.hand.peace:
                draw_retro_text(self.s, "ZIPLA", self.ft, px + 5, gest_y, GREEN, BLACK)
            elif self.hand.fist:
                draw_retro_text(self.s, "ATES ET", self.ft, px + 5, gest_y, RED, BLACK)
            else:
                draw_retro_text(self.s, "HAZIR", self.ft, px + 5, gest_y, WHITE, BLACK)
                
        except: pass

    def _draw_glass_panel(self, x, y, w, h, border_color=(0, 240, 255), bg_color=(10, 10, 30, 205)):
        # Create a translucent surface for glass effect
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill(bg_color)
        
        # Draw subtle top highlight line
        for i in range(h):
            ratio = i / h
            alpha_mod = int(45 * (1 - ratio))
            pygame.draw.line(panel, (255, 255, 255, alpha_mod), (0, i), (w, i))
            
        self.s.blit(panel, (x, y))
        
        # Draw modern retro outer neon glow (multiple thin rectangles with fading alpha)
        for i in range(4, 0, -1):
            alpha = int(50 / i)
            glow_surf = pygame.Surface((w + i*2, h + i*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*border_color, alpha), (0, 0, w + i*2, h + i*2), 1, border_radius=15+i)
            self.s.blit(glow_surf, (x - i, y - i))
            
        # Draw solid sleek border
        pygame.draw.rect(self.s, border_color, (x, y, w, h), 2, border_radius=15)
    
    def _draw_menu_background(self):
        self.menu_time += self.dt
        # Classic NES Super Mario Bros blue sky color
        self.s.fill((92, 148, 252))
        
        # Draw some decorative clouds and hills
        for hx, hy, hw, hh in [(150, SH-120, 240, 90), (750, SH-140, 320, 110), (1050, SH-110, 180, 80)]:
            pygame.draw.ellipse(self.s, MOUNTAIN_FAR, (hx, hy, hw, hh))
        for hx, hy, hw, hh in [(50, SH-100, 160, 70), (450, SH-130, 200, 100), (900, SH-100, 150, 70)]:
            pygame.draw.ellipse(self.s, HILL_FAR, (hx, hy, hw, hh))
            
        # Draw clouds
        for cx, cy, cw in [(100, 80, 120), (500, 60, 150), (950, 90, 130), (300, 120, 100), (750, 100, 110)]:
            bx = (cx - self.menu_time * 8) % (SW + cw) - cw
            ch = cw // 3
            for dx, dy, dw, dh in [(0, ch//2, cw, ch), (cw//4, 0, cw//2, ch)]:
                pygame.draw.ellipse(self.s, CLOUD_SHADOW, (bx+dx+2, cy+dy+2, dw, dh))
                pygame.draw.ellipse(self.s, CLOUD_COLOR, (bx+dx, cy+dy, dw, dh))
                
        # Draw ground tiles at the bottom of the screen
        for x in range(0, SW + 32, 32):
            draw_brick(self.s, x, SH - 32)
            draw_brick(self.s, x, SH - 64)
            
    def _execute_menu_action(self, index):
        SoundGenerator.click_sound(self.master_volume)
        if index == 0:
            self.last_checkpoint = None
            self.level = 1
            self._build()
            self.score = 0; self.coins_c = 0
            self.lives = LIVES; self.kills = 0
            self.state = State.PLAY
            self.st = time.time()
            self.transition_alpha = 1
            self.transition_dir = 1
        elif index == 1:
            self.state = State.CONTROLS
        elif index == 2:
            self._enter_settings()
        elif index == 3:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _menu(self):
        self._draw_menu_background()
        
        # 1. Title Logo with 3D shadow layers
        title_y = 80 + math.sin(self.menu_time * 1.5) * 5
        title_text = "SUPER MARIO BROS"
        # Deep 3D Shadow Layers (Dark Red -> Orange -> Gold Highlight -> White Core)
        draw_retro_text(self.s, title_text, self.fl, SW//2 - 324, title_y + 4, (100, 0, 0), BLACK)
        draw_retro_text(self.s, title_text, self.fl, SW//2 - 322, title_y + 2, (255, 100, 0), BLACK)
        draw_retro_text(self.s, title_text, self.fl, SW//2 - 320, title_y, RED, BLACK)
        
        # Subtitle
        sub_text = "ULTIMATE EDITION v3.2.2"
        sub_y = title_y + 70
        draw_retro_text(self.s, sub_text, self.fb, SW//2 - 242, sub_y + 2, (150, 100, 0), BLACK)
        draw_retro_text(self.s, sub_text, self.fb, SW//2 - 240, sub_y, GOLD, BLACK)
        
        # 2. Premium Retro Menu Board
        bx, by, bw, bh = SW//2 - 230, 240, 460, 310
        ctrl_label = f"KONTROL: {'EL TAKIBI' if self.control_mode == 1 else 'KLAVYE'}"
        draw_retro_text(self.s, ctrl_label, self.ft, bx + 50, by - 24, GOLD, BLACK)
        self._draw_retro_dialog(bx, by, bw, bh)
        
        # Decorative Q-blocks inside the menu board corners
        draw_qblock(self.s, bx + 16, by + 16, False)
        draw_qblock(self.s, bx + bw - 48, by + 16, False)
        draw_qblock(self.s, bx + 16, by + bh - 48, True)
        draw_qblock(self.s, bx + bw - 48, by + bh - 48, True)
        
        # Render options
        options = ["OYUNA BASLA", "KONTROLLER", "AYARLAR", "CIKIS"]
        mp = pygame.mouse.get_pos()
        mc = self.mouse_clicked
        
        for i, opt in enumerate(options):
            y_pos = 275 + i * 60
            
            # Hover detection relative to menu board
            if bx + 50 <= mp[0] <= bx + bw - 50 and y_pos - 5 <= mp[1] <= y_pos + 40:
                if self.menu_selected != i:
                    self.menu_selected = i
                    SoundGenerator.hover_sound(self.master_volume)
                if mc:
                    self._execute_menu_action(i)
                    
            color = GOLD if i == self.menu_selected else WHITE
            draw_retro_text(self.s, opt, self.fm, SW//2 - 100, y_pos, color, BLACK)
            
            if i == self.menu_selected:
                draw_menu_mushroom(self.s, SW//2 - 145, y_pos + 5, 28)
                
        if self.hs > 0:
            draw_retro_text(self.s, f"EN YUKSEK SKOR: {self.hs:06d}", self.fs, SW//2 - 120, 565, GOLD)
            
        if self.max_combo_record > 0:
            draw_retro_text(self.s, f"En Yuksek Combo: x{self.max_combo_record}", self.ft, SW//2 - 80, 600, LIGHT_GRAY)
            
        info = self.ft.render("YON TUSLARI: Sec | ENTER: Onayla | ESC: Cikis | R: Yeniden Baslat | C: Kontrol Degistir", True, WHITE)
        self.s.blit(info, info.get_rect(center=(SW//2, SH-15)))
    
    def _controls_screen(self):
        self._draw_menu_background()
        
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ov.fill((0, 0, 20, 100))
        self.s.blit(ov, (0, 0))
        
        # Enclose controls in a stunning glassmorphic panel
        self._draw_glass_panel(SW//2 - 340, 95, 680, 520, (0, 240, 255))
        
        title = self.fl.render("KONTROLLER", True, GOLD)
        # Gold glowing outline for controls title
        for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            glow_t = self.fl.render("KONTROLLER", True, (255, 100, 0))
            self.s.blit(glow_t, (SW//2 - glow_t.get_width()//2 + dx, 55 - glow_t.get_height()//2 + dy))
        self.s.blit(title, title.get_rect(center=(SW//2, 55)))
        
        controls = [
            ("El Hareketi", "Saga / Sola hareket"),
            ("Peace Isareti", "Ziplama"),
            ("Yukari Konum", "Hizli kosma"),
            ("Asagi Konum", "Comelme / Ground Pound"),
            ("Klavye Yon Tuslari", "Hareket (LEFT/RIGHT)"),
            ("SPACE / UP / W", "Ziplama"),
            ("P Tusu", "Duraklat"),
            ("R Tusu", "Yeniden Baslat"),
            ("F Tusu", "Tam Ekran"),
            ("ESC", "Menu"),
            ("X Tusu (Fire Power)", "Ates Topu"),
            ("1 Tusu", "Hava Durumu Degistir"),
        ]
        
        y = 115
        for name, desc in controls:
            name_txt = self.fs.render(name, True, (0, 240, 255))
            arrow_txt = self.fs.render(":", True, WHITE)
            desc_txt = self.fs.render(desc, True, WHITE)
            
            self.s.blit(name_txt, (SW//2 - 300, y))
            self.s.blit(arrow_txt, (SW//2 + 50, y))
            self.s.blit(desc_txt, (SW//2 + 70, y))
            y += 40
        
        mp = pygame.mouse.get_pos()
        mc = self.mouse_clicked
        back_btn = Button(SW//2-120, SH-80, 240, 55, "GERI DON", "back",
                         DARK_GRAY, (100, 100, 100), WHITE, 40)
        if back_btn.is_clicked(mp, mc):
            self.state = State.MENU
        back_btn.draw(self.s, mp, self.fm)
    
    def _settings_screen(self):
        self._draw_menu_background()
        
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ov.fill((0, 0, 20, 100))
        self.s.blit(ov, (0, 0))
        
        # Enclose settings buttons in a gorgeous glass panel
        self._draw_glass_panel(SW//2 - 280, 120, 560, 450, (0, 240, 255))
        
        title = self.fl.render("AYARLAR", True, GOLD)
        # glowing yellow/orange outline for the settings title
        for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            glow_t = self.fl.render("AYARLAR", True, (255, 100, 0))
            self.s.blit(glow_t, (SW//2 - glow_t.get_width()//2 + dx, 55 - glow_t.get_height()//2 + dy))
        self.s.blit(title, title.get_rect(center=(SW//2, 55)))
        
        desc = self.ft.render("Ayarlari degistirmek icin < > tuslarini kullanin veya tiklayin", 
                              True, (180, 180, 180))
        self.s.blit(desc, desc.get_rect(center=(SW//2, 105)))
        
        mp = pygame.mouse.get_pos()
        mc = self.mouse_clicked
        # Settings keyboard events are now handled in the main event loop to prevent lag and double-triggering.
        
        for i, sb in enumerate(self.settings_buttons):
            sb.draw(self.s, self.fs, i == self.settings_selected)
            
            if mc:
                if sb.is_clicked_left(mp):
                    sb.change_value(-1)
                elif sb.is_clicked_right(mp):
                    sb.change_value(1)
        
        if self.settings_back_btn.is_clicked(mp, mc):
            self._apply_settings()
            self.state = State.MENU
        self.settings_back_btn.draw(self.s, mp, self.fm)
        
        hint = self.ft.render("Klavye: YUKARI/ASAGI sec, SOL/SAG degistir | Mouse: < > butonlarina tikla", 
                              True, (120, 120, 120))
        self.s.blit(hint, hint.get_rect(center=(SW//2, SH-25)))
    
    def _draw_retro_dialog(self, x, y, w, h):
        pygame.draw.rect(self.s, BLACK, (x, y, w, h))
        pygame.draw.rect(self.s, WHITE, (x, y, w, h), 4)
        pygame.draw.rect(self.s, BLACK, (x + 6, y + 6, w - 12, h - 12))
        pygame.draw.rect(self.s, WHITE, (x + 8, y + 8, w - 16, h - 16), 2)

    def _execute_pause_action(self, index):
        SoundGenerator.click_sound(self.master_volume)
        if index == 0:
            self.state = State.PLAY
        elif index == 1:
            self.last_checkpoint = None
            self._build()
            self.score = 0; self.coins_c = 0
            self.lives = LIVES; self.kills = 0
            self.state = State.PLAY
            self.st = time.time()
        elif index == 2:
            self.state = State.MENU

    def _pause(self):
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 120))
        self.s.blit(ov, (0, 0))
        
        self._draw_retro_dialog(SW//2 - 210, 110, 420, 360)
        draw_retro_text(self.s, "DURAKLATILDI", self.fb, SW//2 - 160, 150, WHITE, BLACK)
        
        options = ["DEVAM ET", "YENIDEN BASLAT", "ANA MENU"]
        mp = pygame.mouse.get_pos()
        mc = self.mouse_clicked
        
        for i, opt in enumerate(options):
            y_pos = 240 + i * 65
            if SW//2 - 180 <= mp[0] <= SW//2 + 180 and y_pos - 10 <= mp[1] <= y_pos + 40:
                if self.pause_selected != i:
                    self.pause_selected = i
                    SoundGenerator.hover_sound(self.master_volume)
                if mc:
                    self._execute_pause_action(i)
                    
            color = GOLD if i == self.pause_selected else WHITE
            draw_retro_text(self.s, opt, self.fm, SW//2 - 110, y_pos, color, BLACK)
            
            if i == self.pause_selected:
                draw_menu_mushroom(self.s, SW//2 - 155, y_pos + 5, 28)
                
        info = self.ft.render("YON TUSLARI: Sec | ENTER: Onayla | P: Devam", True, WHITE)
        self.s.blit(info, info.get_rect(center=(SW//2, SH-25)))

    def _execute_over_action(self, index):
        SoundGenerator.click_sound(self.master_volume)
        if index == 0:
            self.last_checkpoint = None
            self._build()
            self.score = 0; self.coins_c = 0
            self.lives = LIVES; self.kills = 0
            self.state = State.PLAY
            self.st = time.time()
        elif index == 1:
            self.state = State.MENU

    def _gameover(self):
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        self.s.blit(ov, (0, 0))
        
        self._draw_retro_dialog(SW//2 - 210, 60, 420, 520)
        draw_retro_text(self.s, "GAME OVER", self.fb, SW//2 - 130, 90, RED, BLACK)
        
        stats = [
            f"★ Skor: {self.score:06d}",
            f"🪙 Coin: {self.coins_c % 100}",
            f"💀 Dusman: {self.kills}",
        ]
        if self.p and self.p.max_combo > 0:
            stats.append(f"🔥 Max Combo: x{self.p.max_combo}")
            
        y = 170
        for stat in stats:
            draw_retro_text(self.s, stat, self.fm, SW//2 - 120, y, WHITE, BLACK)
            y += 45
            
        if self.score >= self.hs and self.score > 0:
            draw_retro_text(self.s, "YENI REKOR!", self.fs, SW//2 - 90, y + 10, GOLD, BLACK)
            
        options = ["YENIDEN DENE", "ANA MENU"]
        mp = pygame.mouse.get_pos()
        mc = self.mouse_clicked
        
        for i, opt in enumerate(options):
            y_pos = 380 + i * 65
            if SW//2 - 180 <= mp[0] <= SW//2 + 180 and y_pos - 10 <= mp[1] <= y_pos + 40:
                if self.over_selected != i:
                    self.over_selected = i
                    SoundGenerator.hover_sound(self.master_volume)
                if mc:
                    self._execute_over_action(i)
                    
            color = GOLD if i == self.over_selected else WHITE
            draw_retro_text(self.s, opt, self.fm, SW//2 - 110, y_pos, color, BLACK)
            
            if i == self.over_selected:
                draw_menu_mushroom(self.s, SW//2 - 155, y_pos + 5, 28)
                
        info = self.ft.render("YON TUSLARI: Sec | ENTER: Onayla | SPACE: Yeniden Oyna", True, WHITE)
        self.s.blit(info, info.get_rect(center=(SW//2, SH-25)))

    def _win_screen(self):
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 130))
        self.s.blit(ov, (0, 0))
        
        self._draw_retro_dialog(SW//2 - 240, 80, 480, 500)
        draw_retro_text(self.s, "SEVIYE TAMAM!", self.fb, SW//2 - 160, 110, GOLD, BLACK)
        
        time_bonus = max(0, int(LVL_TIME - self.gt) * 10)
        
        # Prevent double adding of time bonus to score on repeated frames
        if not hasattr(self, '_time_bonus_applied') or not self._time_bonus_applied:
            self.score += time_bonus
            self._time_bonus_applied = True
            
        stats = [
            f"★ Seviye Skoru: {self.score - time_bonus:06d}",
            f"⏱ Sure Bonus: +{time_bonus}",
            f"✨ Toplam Skor: {self.score:06d}",
            f"🪙 Alinan Coin: {self.coins_c}",
            f"💀 Oldurulen Dusman: {self.kills}",
        ]
        
        y = 195
        for stat in stats:
            color = GREEN if "Bonus" in stat or "Toplam" in stat else WHITE
            draw_retro_text(self.s, stat, self.fm, SW//2 - 140, y, color, BLACK)
            y += 45
            
        if self.score > self.hs:
            self.hs = self.score
            draw_retro_text(self.s, "YENI REKOR!", self.fs, SW//2 - 90, y + 15, GOLD, BLACK)
            
        info = self.ft.render("ENTER: Sonraki Seviye | SPACE: Yeniden Oyna | ESC: Menu", True, WHITE)
        self.s.blit(info, info.get_rect(center=(SW//2, SH-40)))
    def run(self):
        print("  ULTIMATE MARIO v3.2.2 BASLATILIYOR...")
        print("  Tum hatalar duzeltildi - MUSH_S sorunu cozuldu\n")
        
        running = True
        lt = time.time()
        
        while running:
            self.dt = min(time.time() - lt, 0.05)
            lt = time.time()
            
            self.mouse_clicked = False
            
            if self.state == State.PLAY:
                if self.control_mode == 1 and self.hand is not None:
                    self.hand.update()
                self._input()
                self._update(self.dt)
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        self.mouse_clicked = True
                
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        if self.state in [State.PAUSE, State.OVER, State.CONTROLS, 
                                         State.WIN, State.SETTINGS]:
                            self.state = State.MENU
                        elif self.state == State.MENU:
                            running = False
                        else:
                            running = False
                    
                    elif e.key == pygame.K_c:
                        if self.state == State.MENU:
                            self.control_mode = 1 - self.control_mode
                            if self.control_mode == 0:
                                if self.hand is not None:
                                    self.hand.stop_capture()
                            else:
                                if self.hand is None:
                                    self.hand = HandTracker(self.selected_cam_index)
                                self.hand.start_capture()
                            SoundGenerator.click_sound(self.master_volume)
                            
                    elif e.key == pygame.K_UP:
                        if self.state == State.MENU:
                            self.menu_selected = (self.menu_selected - 1) % 4
                            SoundGenerator.hover_sound(self.master_volume)
                        elif self.state == State.PAUSE:
                            self.pause_selected = (self.pause_selected - 1) % 3
                            SoundGenerator.hover_sound(self.master_volume)
                        elif self.state == State.OVER:
                            self.over_selected = (self.over_selected - 1) % 2
                            SoundGenerator.hover_sound(self.master_volume)
                        elif self.state == State.SETTINGS:
                            self.settings_selected = (self.settings_selected - 1) % len(self.settings_buttons)
                            SoundGenerator.hover_sound(self.master_volume)
                            
                    elif e.key == pygame.K_DOWN:
                        if self.state == State.MENU:
                            self.menu_selected = (self.menu_selected + 1) % 4
                            SoundGenerator.hover_sound(self.master_volume)
                        elif self.state == State.PAUSE:
                            self.pause_selected = (self.pause_selected + 1) % 3
                            SoundGenerator.hover_sound(self.master_volume)
                        elif self.state == State.OVER:
                            self.over_selected = (self.over_selected + 1) % 2
                            SoundGenerator.hover_sound(self.master_volume)
                        elif self.state == State.SETTINGS:
                            self.settings_selected = (self.settings_selected + 1) % len(self.settings_buttons)
                            SoundGenerator.hover_sound(self.master_volume)
                            
                    elif e.key == pygame.K_LEFT:
                        if self.state == State.SETTINGS:
                            self.settings_buttons[self.settings_selected].change_value(-1)
                            
                    elif e.key == pygame.K_RIGHT:
                        if self.state == State.SETTINGS:
                            self.settings_buttons[self.settings_selected].change_value(1)
                    
                    elif e.key == pygame.K_SPACE:
                        if self.state in [State.MENU, State.OVER, State.WIN]:
                            self.last_checkpoint = None
                            self.level = 1
                            self._time_bonus_applied = False
                            self._build()
                            self.score = 0; self.coins_c = 0
                            self.lives = LIVES; self.kills = 0
                            self.state = State.PLAY
                            self.st = time.time()
                            self.transition_alpha = 1
                            self.transition_dir = 1
                    
                    elif e.key == pygame.K_RETURN:
                        if self.state == State.MENU:
                            self._execute_menu_action(self.menu_selected)
                        elif self.state == State.PAUSE:
                            self._execute_pause_action(self.pause_selected)
                        elif self.state == State.OVER:
                            self._execute_over_action(self.over_selected)
                        elif self.state == State.WIN:
                            self.level += 1
                            self._time_bonus_applied = False
                            self.last_checkpoint = None
                            self._build()
                            self.lives = min(9, self.lives + 1)  # Bonus life for clearing level!
                            self.state = State.PLAY
                            self.st = time.time()
                            self.transition_alpha = 1
                            self.transition_dir = 1
                    
                    elif e.key == pygame.K_p:
                        if self.state == State.PLAY:
                            self.state = State.PAUSE
                        elif self.state == State.PAUSE:
                            self.state = State.PLAY
                    
                    elif e.key == pygame.K_r:
                        if self.state != State.MENU:
                            self.last_checkpoint = None
                            self._build()
                            self.score = 0; self.coins_c = 0
                            self.lives = LIVES; self.kills = 0
                            self.state = State.PLAY
                            self.st = time.time()
                    
                    elif e.key == pygame.K_f:
                        self.fullscreen = not self.fullscreen
                        pygame.display.toggle_fullscreen()
                    
                    elif e.key == pygame.K_1 and self.state == State.PLAY:
                        self.weather = Weather((self.weather.value + 1) % 4)
                        self.weather_timer = 999
                    
                    elif e.key == pygame.K_x and self.state == State.PLAY and self.p and self.p.power == PowerUp.FIRE:
                        if len(self.fireballs) < 3:
                            fb_vx = 8 if self.p.dir == Dir.RIGHT else -8
                            self.fireballs.append(Fireball(
                                self.p.x + self.p.w//2, self.p.y + self.p.h//2,
                                fb_vx, -2
                            ))
            
            self._render()
            self.clock.tick(FPS)
        
        if self.hand is not None:
            self.hand.release()
        pygame.quit()
        cv2.destroyAllWindows()
        print(f"\n  Oyun kapandi. En yuksek skor: {self.hs:,}\n")
        sys.exit(0)

def main():
    try:
        MarioUltimate().run()
    except KeyboardInterrupt:
        print("\n  [Warn] Oyun kullanici tarafindan durduruldu.")
    except Exception as e:
        print(f"\n  [Error] Kritik hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        cv2.destroyAllWindows()
        sys.exit(0)

if __name__ == "__main__":
    main()
