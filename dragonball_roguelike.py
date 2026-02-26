import math
import os
import random
from dataclasses import dataclass

import pygame

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    print("Warning: mixer de audio no disponible")

TITLE = "Dragonball Roguelike – Ultimate Edition"
WIDTH, HEIGHT = 1000, 660
MAP_WIDTH, MAP_HEIGHT = 2400, 1600
FPS = 60
PLAYER_SIZE = (44, 64)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 40, 40)
GREEN = (50, 205, 50)
BLUE = (50, 120, 255)
YELLOW = (255, 220, 50)
DARK = (20, 20, 20)
GRAY = (110, 110, 110)
ORANGE = (255, 140, 40)
PURPLE = (150, 50, 200)
PALE = (220, 220, 220)
CYAN = (50, 220, 220)
PINK = (255, 100, 180)

pygame.display.set_caption(TITLE)
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
FONT = pygame.font.SysFont("consolas", 17)
FONT_SM = pygame.font.SysFont("consolas", 14)
BIGFONT = pygame.font.SysFont("consolas", 32)
MEDFONT = pygame.font.SysFont("consolas", 22)

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def load_image(path, size, fallback_color):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf


def play_bg_music():
    path = os.path.join(SOUND_DIR, "musica.mp3")
    if not pygame.mixer.get_init() or not os.path.exists(path):
        return
    try:
        if pygame.mixer.music.get_busy():
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.65)
        pygame.mixer.music.play(-1)
    except Exception:
        print("Warning: no se pudo reproducir musica.mp3")


def stop_bg_music():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


BASE_PLAYER_ASSETS = {
    "base": ((0, 0, 180)),
    "ki": ((50, 50, 200)),
    "ssj": ((255, 180, 50)),
    "ssj2": ((255, 150, 40)),
    "ssj3": ((255, 110, 40)),
    "ssj4": ((200, 80, 40)),
    "ssj_god": ((200, 50, 200)),
    "ssjblue": ((120, 200, 255)),
    "ssjblue_kaioken": ((200, 120, 255)),
    "ui_senal": ((255, 240, 200)),
    "mui": ((200, 240, 255)),
    "ssjblue_evolution": ((120, 160, 255)),
    "ultra_ego": ((180, 70, 220)),
}

ENEMY_ASSETS = {
    "soldier_melee": ("Soldado_Meele.png", (36, 56), (40, 160, 80)),
    "soldier_sniper": ("Soldado_Sniper.png", (36, 56), (200, 160, 40)),
    "enemy_brute": ("Enemy_Brute.png", (44, 66), (180, 30, 30)),
    "enemy_tank": ("Enemy_Tank.png", (46, 68), (80, 80, 160)),
    "enemy_assassin": ("Enemy_Assassin.png", (36, 56), (40, 160, 200)),
    "boss_beast": ("Boss_Beast.png", (120, 160), (200, 40, 40)),
    "boss_sniper": ("Boss_Sniper.png", (120, 160), (40, 200, 120)),
    "boss_king": ("Boss_King.png", (140, 180), (180, 90, 200)),
}


class AssetManager:
    def __init__(self):
        self.enemy = {}
        for key, (fname, size, col) in ENEMY_ASSETS.items():
            self.enemy[key] = load_image(os.path.join(ASSET_DIR, fname), size, col)

    def load_player_assets(self, character):
        prefix = "Goku" if character == "goku" else "Vegeta"
        mapping = {
            "base": f"{prefix}_Base.png",
            "ki": f"{prefix}_Ki.png",
            "ssj": f"{prefix}_SSJ1.png",
            "ssj2": f"{prefix}_SSJ2.png",
            "ssj3": f"{prefix}_SSJ3.png",
            "ssj4": f"{prefix}_SSJ4.png",
            "ssj_god": f"{prefix}_SSJGOD.png",
            "ssjblue": f"{prefix}_SSJBLUE.png",
            "ssjblue_kaioken": f"{prefix}_SSJBLUEKAIOKEN.png",
            "ui_senal": f"{prefix}_UI_SENAL.png",
            "mui": f"{prefix}_MUI.png",
            "ssjblue_evolution": f"{prefix}_SSJBLUEEVOLUTION.png",
            "ultra_ego": f"{prefix}_ULTRAEGO.png",
        }
        assets = {}
        for key, fname in mapping.items():
            assets[key] = load_image(
                os.path.join(ASSET_DIR, fname), PLAYER_SIZE, BASE_PLAYER_ASSETS[key]
            )
        return assets


ASSETS = AssetManager()


@dataclass
class FormData:
    dmg: float
    spd: float
    drain_ki: float = 0.0
    drain_hp: float = 0.0


GOKU_FORMS = {
    "ssj": FormData(2.0, 1.5, drain_ki=4.0),
    "ssj2": FormData(3.0, 1.9, drain_ki=6.0),
    "ssj3": FormData(5.0, 2.2, drain_ki=12.0),
    "ssj4": FormData(4.0, 2.9, drain_ki=14.0),
    "ssj_god": FormData(7.0, 2.4, drain_ki=25.0),
    "ssjblue": FormData(10.0, 3.1, drain_ki=30.0),
    "ssjblue_kaioken": FormData(15.0, 3.4, drain_ki=40.0, drain_hp=50.0),
    "ui_senal": FormData(17.0, 4.0),
    "mui": FormData(30.0, 5.2, drain_hp=30.0),
}

VEGETA_FORMS = {
    "ssj": FormData(2.3, 1.3, drain_ki=4.0),
    "ssj2": FormData(4.0, 1.5, drain_ki=6.0),
    "ssj3": FormData(6.0, 1.8, drain_ki=9.0),
    "ssj4": FormData(6.4, 2.1, drain_ki=10.0),
    "ssj_god": FormData(8.0, 1.9, drain_ki=12.0),
    "ssjblue": FormData(11.0, 2.6, drain_ki=17.0),
    "ssjblue_evolution": FormData(17.0, 3.6, drain_ki=20.0),
    "ultra_ego": FormData(25.0, 4.0, drain_ki=5.0, drain_hp=3.0),
}


class Projectile:
    def __init__(self, x, y, vx, vy, owner, damage=12, life=220, color=RED, radius=8, pierce=0, grow=0):
        self.rect = pygame.Rect(0, 0, 12, 12)
        self.rect.center = (int(x), int(y))
        self.vx, self.vy = vx, vy
        self.owner = owner
        self.damage = damage
        self.life = life
        self.color = color
        self.radius = radius
        self.pierce = pierce
        self.grow = grow

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        self.life -= 1
        if self.grow:
            self.radius = min(180, self.radius + self.grow)

    def draw(self, surf, camx, camy):
        cx = self.rect.centerx - camx
        cy = self.rect.centery - camy
        pygame.draw.circle(surf, self.color, (cx, cy), self.radius)
        if self.owner == "hakai":
            for i in range(8):
                ang = (pygame.time.get_ticks() * 0.015) + i * (math.tau / 8)
                ex = int(cx + math.cos(ang) * (self.radius + 12))
                ey = int(cy + math.sin(ang) * (self.radius + 12))
                pygame.draw.line(surf, BLACK, (cx, cy), (ex, ey), 2)


class Beam:
    def __init__(self, ox, oy, dx, dy, length, halfw, damage, life=8, color=BLUE):
        self.ox, self.oy, self.dx, self.dy = ox, oy, dx, dy
        self.length, self.halfw = length, halfw
        self.damage, self.life, self.color = damage, life, color

    def update(self):
        self.life -= 1

    def draw(self, surf, camx, camy):
        sx = int(self.ox - camx)
        sy = int(self.oy - camy)
        ex = int(self.ox + self.dx * self.length - camx)
        ey = int(self.oy + self.dy * self.length - camy)
        pygame.draw.line(surf, self.color, (sx, sy), (ex, ey), max(2, self.halfw * 2))

    def hits_enemy(self, enemy):
        px, py = enemy.rect.center
        ex = self.ox + self.dx * self.length
        ey = self.oy + self.dy * self.length
        seg = pygame.Vector2(ex - self.ox, ey - self.oy)
        pt = pygame.Vector2(px - self.ox, py - self.oy)
        seg_l2 = seg.length_squared()
        if seg_l2 == 0:
            return False
        t = clamp(pt.dot(seg) / seg_l2, 0.0, 1.0)
        qx = self.ox + seg.x * t
        qy = self.oy + seg.y * t
        dist2 = (px - qx) ** 2 + (py - qy) ** 2
        return dist2 <= (self.halfw + max(enemy.rect.w, enemy.rect.h) / 2) ** 2


class Player:
    def __init__(self, x, y, character="goku"):
        self.character = character
        self.assets = ASSETS.load_player_assets(character)
        self.rect = pygame.Rect(0, 0, *PLAYER_SIZE)
        self.rect.center = (x, y)
        self.direction = pygame.Vector2(1, 0)
        self.health = self.max_health = 10000.0
        self.ki = self.max_ki = 200.0
        self.base_speed = 4.6
        self.attack_mult = 1.0
        self.transform = None
        self.projectiles = []
        self.beams = []
        self.attack_cd = 0
        self.dash_cd = 0
        self.skill_cd = {}
        self.level = 1

        if character == "goku":
            self.transforms = ["ssj", "ssj2", "ssj3", "ssj4", "ssj_god", "ssjblue", "ssjblue_kaioken", "ui_senal", "mui"]
            self.forms = GOKU_FORMS
            self.active_slots = ["kamehameha", "final_flash", "genkidama", "makankosapo"]
        else:
            self.transforms = ["ssj", "ssj2", "ssj3", "ssj4", "ssj_god", "ssjblue", "ssjblue_evolution", "ultra_ego"]
            self.forms = VEGETA_FORMS
            self.active_slots = ["final_flash_vegeta", "garlick_gun", "big_bang", "transform_next"]

    def dmg_mult(self):
        return self.forms.get(self.transform, FormData(1, 1)).dmg

    def spd_mult(self):
        return self.forms.get(self.transform, FormData(1, 1)).spd

    def update(self):
        self.attack_cd = max(0, self.attack_cd - 1)
        self.dash_cd = max(0, self.dash_cd - 1)
        for k in list(self.skill_cd):
            self.skill_cd[k] = max(0, self.skill_cd[k] - 1)

        if self.transform in self.forms:
            f = self.forms[self.transform]
            self.ki -= f.drain_ki / FPS
            self.health -= f.drain_hp / FPS
            if self.ki <= 0 or self.health <= 0:
                self.end_transform()

        # bonus permanente vegeta SSJGod
        regen_mult = 2.0 if self.character == "vegeta" and self.level >= 1 and getattr(self, "god_passive", False) else 1.0
        self.ki = clamp(self.ki + (0.1 * regen_mult), 0, self.max_ki)
        self.health = clamp(self.health + 1.2 / FPS, 0, self.max_health)

    def move(self, keys):
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        v = pygame.Vector2(dx, dy)
        if v.length_squared() > 0:
            v = v.normalize()
            self.direction = v
            spd = self.base_speed * self.spd_mult()
            self.rect.x += int(v.x * spd)
            self.rect.y += int(v.y * spd)
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))

    def begin_transform(self, form):
        if form not in self.transforms:
            return
        self.transform = form
        if self.character == "vegeta" and form == "ssj_god":
            self.god_passive = True
        if self.character == "vegeta" and form == "ssjblue":
            self.max_ki = 400.0
        else:
            self.max_ki = max(self.max_ki, 200.0)

    def end_transform(self):
        self.transform = None
        if self.character == "vegeta":
            self.max_ki = max(200.0, min(self.max_ki, 400.0))

    def next_transform(self):
        if not self.transforms:
            return
        if self.transform not in self.transforms:
            self.begin_transform(self.transforms[0])
            return
        i = self.transforms.index(self.transform)
        if i + 1 < len(self.transforms):
            self.begin_transform(self.transforms[i + 1])
        else:
            self.end_transform()

    def _target_dir(self, enemies):
        if enemies:
            e = min(enemies, key=lambda x: pygame.Vector2(x.rect.center).distance_to(self.rect.center))
            v = pygame.Vector2(e.rect.center) - pygame.Vector2(self.rect.center)
            if v.length_squared() > 0:
                return v.normalize()
        return pygame.Vector2(self.direction)

    def cast_active(self, slot, enemies):
        key = self.active_slots[slot] if slot < len(self.active_slots) else None
        if not key:
            return
        if key == "transform_next":
            self.next_transform()
            return
        if key == "kamehameha":
            self.cast_beam(enemies, 1200, 30, 140, 60, 18, BLUE)
        elif key == "final_flash":
            self.cast_beam(enemies, 1400, 40, 220, 130, 28, YELLOW)
        elif key == "genkidama":
            self.cast_genkidama()
        elif key == "makankosapo":
            self.cast_beam(enemies, 900, 12, 100, 30, 12, PURPLE)
        elif key == "final_flash_vegeta":
            self.cast_final_flash_vegeta(enemies)
        elif key == "garlick_gun":
            self.cast_beam(enemies, 760, 20, 180, 70, 18, PURPLE)
        elif key == "big_bang":
            self.cast_big_bang(enemies)

    def cast_beam(self, enemies, length, halfw, dmg, cost, cd, color):
        if self.attack_cd > 0 or self.ki < cost:
            return
        d = self._target_dir(enemies)
        beam = Beam(self.rect.centerx, self.rect.centery, d.x, d.y, length, halfw, int(dmg * self.dmg_mult()), 8, color)
        self.beams.append(beam)
        for e in enemies:
            if e.alive and beam.hits_enemy(e):
                e.take_damage(beam.damage)
        self.ki -= cost
        self.attack_cd = cd

    def cast_final_flash_vegeta(self, enemies):
        if self.attack_cd > 0 or self.ki < 190:
            return
        d = self._target_dir(enemies)
        p = pygame.Vector2(-d.y, d.x) * 12
        for s in (1, -1):
            beam = Beam(self.rect.centerx + p.x * s, self.rect.centery + p.y * s, d.x, d.y, 1500, 42, int(280 * self.dmg_mult()), 10, YELLOW)
            self.beams.append(beam)
            for e in enemies:
                if e.alive and beam.hits_enemy(e):
                    e.take_damage(beam.damage)
        self.ki -= 190
        self.attack_cd = 28

    def cast_big_bang(self, enemies):
        if self.skill_cd.get("big_bang", 0) or self.ki < 120:
            return
        d = self._target_dir(enemies)
        p = Projectile(self.rect.centerx, self.rect.centery, d.x * 9, d.y * 9, "player", int(90 * self.dmg_mult()), 130, BLUE, radius=12)
        p.big_bang = True
        self.projectiles.append(p)
        self.ki -= 120
        self.skill_cd["big_bang"] = 120

    def cast_genkidama(self):
        if self.skill_cd.get("genkidama", 0) or self.ki < 120:
            return
        p = Projectile(self.rect.centerx + self.direction.x * 100, self.rect.centery + self.direction.y * 100, 0, 0, "player", int(240 * self.dmg_mult()), 100, CYAN, radius=140)
        self.projectiles.append(p)
        self.ki -= 120
        self.skill_cd["genkidama"] = 180

    def cast_hakai(self):
        if self.character != "vegeta" or self.transform != "ultra_ego":
            return
        if self.skill_cd.get("hakai", 0) or self.ki < 250:
            return
        d = pygame.Vector2(self.direction)
        if d.length_squared() == 0:
            d = pygame.Vector2(1, 0)
        d = d.normalize()
        self.projectiles.append(Projectile(self.rect.centerx, self.rect.centery, d.x * 16, d.y * 16, "hakai", 999999, 280, PURPLE, radius=18, pierce=99999, grow=0.6))
        self.ki -= 250
        self.skill_cd["hakai"] = 180

    def draw(self, surf, camx, camy):
        key = self.transform if self.transform in self.assets else "base"
        surf.blit(self.assets[key], (self.rect.x - camx, self.rect.y - camy))


class Enemy:
    def __init__(self, x, y, kind="chaser", level=1):
        self.kind = kind
        self.level = level
        key = {
            "chaser": "soldier_melee",
            "ranged": "soldier_sniper",
            "brute": "enemy_brute",
            "tank": "enemy_tank",
            "assassin": "enemy_assassin",
        }[kind]
        self.image = ASSETS.enemy[key]
        self.rect = self.image.get_rect(center=(x, y))
        base = {"chaser": 50, "ranged": 40, "brute": 100, "tank": 220, "assassin": 35}[kind]
        self.health = self.max_health = base + level * 20
        self.speed = {"chaser": 1.8, "ranged": 1.0, "brute": 1.0, "tank": 0.6, "assassin": 2.4}[kind]
        self.alive = True
        self.attack_timer = random.randint(20, 80)

    def take_damage(self, dmg):
        if not self.alive:
            return
        self.health -= dmg
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def update(self, player, global_proj):
        if not self.alive:
            return
        d = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        l = d.length()
        if l > 0:
            d = d.normalize()
        if self.kind in ("chaser", "brute", "assassin"):
            self.rect.x += int(d.x * self.speed)
            self.rect.y += int(d.y * self.speed)
        else:
            if l > 260:
                self.rect.x += int(d.x * self.speed)
                self.rect.y += int(d.y * self.speed)
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                global_proj.append(Projectile(self.rect.centerx, self.rect.centery, d.x * 5, d.y * 5, "enemy", 20 + self.level * 2, 180, YELLOW, radius=6))
                self.attack_timer = random.randint(50, 120)
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))

    def draw(self, surf, camx, camy):
        if not self.alive:
            return
        surf.blit(self.image, (self.rect.x - camx, self.rect.y - camy))
        ratio = self.health / self.max_health
        pygame.draw.rect(surf, RED, (self.rect.x - camx, self.rect.y - camy - 6, self.rect.w, 5))
        pygame.draw.rect(surf, GREEN, (self.rect.x - camx, self.rect.y - camy - 6, int(self.rect.w * ratio), 5))


class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.state = "menu"
        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2, "goku")
        self.enemies = []
        self.global_projectiles = []
        self.camera_x = self.camera_y = 0
        self.game_time = 0
        self.menu_button = pygame.Rect(WIDTH // 2 - 140, HEIGHT // 2 + 40, 280, 64)
        self.char_goku_btn = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 + 40, 180, 70)
        self.char_vegeta_btn = pygame.Rect(WIDTH // 2 + 40, HEIGHT // 2 + 40, 180, 70)
        self.bg_tiles = [(x, y, random.randint(65, 115)) for x in range(0, MAP_WIDTH, 120) for y in range(0, MAP_HEIGHT, 120)]
        for _ in range(8):
            self.spawn_enemy()

    def spawn_enemy(self):
        px, py = self.player.rect.center
        ang = random.random() * math.tau
        r = random.randint(250, 480)
        x = clamp(int(px + math.cos(ang) * r), 50, MAP_WIDTH - 50)
        y = clamp(int(py + math.sin(ang) * r), 50, MAP_HEIGHT - 50)
        self.enemies.append(Enemy(x, y, random.choice(["chaser", "chaser", "ranged", "brute", "tank", "assassin"]), max(1, 1 + self.game_time // (FPS * 30))))

    def reset_run(self, character):
        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2, character)
        self.enemies.clear()
        self.global_projectiles.clear()
        self.game_time = 0
        self.camera_x = self.camera_y = 0
        for _ in range(8):
            self.spawn_enemy()
        play_bg_music()  # música suena justo al arrancar partida

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.menu_button.collidepoint(event.pos):
                    self.state = "char_select"
                continue
            if self.state == "char_select":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.char_goku_btn.collidepoint(event.pos):
                        self.reset_run("goku")
                        self.state = "playing"
                    elif self.char_vegeta_btn.collidepoint(event.pos):
                        self.reset_run("vegeta")
                        self.state = "playing"
                continue

            if self.state == "playing" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                    stop_bg_music()
                if event.key == pygame.K_r:
                    self.player.cast_active(0, [e for e in self.enemies if e.alive])
                if event.key == pygame.K_t:
                    self.player.cast_active(1, [e for e in self.enemies if e.alive])
                if event.key == pygame.K_y:
                    self.player.cast_active(2, [e for e in self.enemies if e.alive])
                if event.key == pygame.K_q:
                    self.player.cast_active(3, [e for e in self.enemies if e.alive])
                if event.key == pygame.K_c:
                    self.player.cast_hakai()
                if event.key == pygame.K_f:
                    self.player.next_transform()
                if event.key == pygame.K_g and self.player.attack_cd == 0 and self.player.ki >= 8:
                    d = self.player._target_dir([e for e in self.enemies if e.alive])
                    self.player.projectiles.append(Projectile(self.player.rect.centerx, self.player.rect.centery, d.x * 10, d.y * 10, "player", int(26 * self.player.dmg_mult()), 120, RED, radius=8))
                    self.player.ki -= 8
                    self.player.attack_cd = 6
        return True

    def update(self):
        self.clock.tick(FPS)
        if not self.handle_events():
            return False
        if self.state != "playing":
            return True

        self.game_time += 1
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        self.player.update()

        for e in self.enemies:
            e.update(self.player, self.global_projectiles)
            if e.alive and e.rect.colliderect(self.player.rect):
                self.player.health -= 5

        for p in self.global_projectiles[:]:
            p.update()
            if p.life <= 0:
                self.global_projectiles.remove(p)
                continue
            if p.owner == "enemy" and p.rect.colliderect(self.player.rect):
                self.player.health -= p.damage
                self.global_projectiles.remove(p)

        for p in self.player.projectiles[:]:
            p.update()
            if p.life <= 0:
                self.player.projectiles.remove(p)
                continue
            for e in self.enemies:
                if not e.alive:
                    continue
                dist = pygame.Vector2(e.rect.center).distance_to(p.rect.center)
                if dist <= p.radius + max(e.rect.w, e.rect.h) * 0.35:
                    if p.owner == "hakai":
                        e.take_damage(10**9)
                    elif getattr(p, "big_bang", False):
                        e.take_damage(p.damage)
                        self.player.projectiles.append(Projectile(p.rect.centerx, p.rect.centery, 0, 0, "player", int(120 * self.player.dmg_mult()), 120, CYAN, radius=140))
                        if p in self.player.projectiles:
                            self.player.projectiles.remove(p)
                        break
                    else:
                        e.take_damage(p.damage)
                        if p.pierce > 0:
                            p.pierce -= 1
                        else:
                            if p in self.player.projectiles:
                                self.player.projectiles.remove(p)
                            break

        for b in self.player.beams[:]:
            b.update()
            for e in self.enemies:
                if e.alive and b.hits_enemy(e):
                    e.take_damage(b.damage)
            if b.life <= 0:
                self.player.beams.remove(b)

        self.enemies = [e for e in self.enemies if e.alive]
        if len(self.enemies) < 20 and self.game_time % 30 == 0:
            self.spawn_enemy()

        target_x = clamp(self.player.rect.centerx - WIDTH // 2, 0, MAP_WIDTH - WIDTH)
        target_y = clamp(self.player.rect.centery - HEIGHT // 2, 0, MAP_HEIGHT - HEIGHT)
        self.camera_x += int((target_x - self.camera_x) * 0.15)
        self.camera_y += int((target_y - self.camera_y) * 0.15)

        if self.player.health <= 0:
            self.state = "menu"
            stop_bg_music()
        return True

    def draw_world(self):
        SCREEN.fill((70, 115, 75))
        for x, y, hue in self.bg_tiles:
            sx, sy = x - self.camera_x, y - self.camera_y
            if -120 <= sx <= WIDTH + 120 and -120 <= sy <= HEIGHT + 120:
                pygame.draw.rect(SCREEN, (hue, int(hue * 0.88), int(hue * 0.48)), (sx, sy, 120, 120))

        for e in self.enemies:
            e.draw(SCREEN, self.camera_x, self.camera_y)
        for p in self.global_projectiles:
            p.draw(SCREEN, self.camera_x, self.camera_y)
        for p in self.player.projectiles:
            p.draw(SCREEN, self.camera_x, self.camera_y)
        for b in self.player.beams:
            b.draw(SCREEN, self.camera_x, self.camera_y)
        self.player.draw(SCREEN, self.camera_x, self.camera_y)

        pygame.draw.rect(SCREEN, DARK, (12, HEIGHT - 84, 360, 72))
        pygame.draw.rect(SCREEN, RED, (20, HEIGHT - 72, 320, 14))
        pygame.draw.rect(SCREEN, GREEN, (20, HEIGHT - 72, int(320 * (self.player.health / self.player.max_health)), 14))
        pygame.draw.rect(SCREEN, BLUE, (20, HEIGHT - 50, int(320 * (self.player.ki / self.player.max_ki)), 12))
        SCREEN.blit(FONT_SM.render(f"{self.player.character.upper()}  Forma: {self.player.transform or 'base'}", True, WHITE), (20, HEIGHT - 34))
        if self.player.character == "vegeta" and self.player.transform == "ultra_ego":
            SCREEN.blit(FONT_SM.render("C: HAKAI (250 KI)", True, PURPLE), (380, HEIGHT - 34))

    def draw_menu(self):
        SCREEN.fill((14, 14, 24))
        title = BIGFONT.render(TITLE, True, (255, 210, 60))
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 130))
        pygame.draw.rect(SCREEN, (50, 130, 210), self.menu_button, border_radius=12)
        pygame.draw.rect(SCREEN, WHITE, self.menu_button, 2, border_radius=12)
        lbl = BIGFONT.render("JUGAR", True, WHITE)
        SCREEN.blit(lbl, (self.menu_button.centerx - lbl.get_width() // 2, self.menu_button.centery - lbl.get_height() // 2))

    def draw_character_select(self):
        SCREEN.fill((20, 20, 34))
        t = BIGFONT.render("Selecciona personaje", True, YELLOW)
        SCREEN.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 120))

        for rect, name, col in [
            (self.char_goku_btn, "GOKU", BLUE),
            (self.char_vegeta_btn, "VEGETA", PURPLE),
        ]:
            pygame.draw.rect(SCREEN, col, rect, border_radius=10)
            pygame.draw.rect(SCREEN, WHITE, rect, 2, border_radius=10)
            lbl = MEDFONT.render(name, True, WHITE)
            SCREEN.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.centery - lbl.get_height() // 2))

        goku_txt = FONT_SM.render("Goku: árbol original (Kamehameha/UI/MUI)", True, PALE)
        veg_txt = FONT_SM.render("Vegeta: Final Flash/Garlick/Big Bang + Ultra Ego", True, PALE)
        SCREEN.blit(goku_txt, (WIDTH // 2 - goku_txt.get_width() // 2, HEIGHT // 2 + 130))
        SCREEN.blit(veg_txt, (WIDTH // 2 - veg_txt.get_width() // 2, HEIGHT // 2 + 150))

    def run(self):
        running = True
        while running:
            running = self.update()
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "char_select":
                self.draw_character_select()
            else:
                self.draw_world()
            pygame.display.flip()
        stop_bg_music()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
