import pygame
import random
import os
from persistence import load_settings

# Path to assets folder (same directory as this file)
ASSETS = os.path.join(os.path.dirname(__file__), "assets")

def load_img(name, size=None, remove_white_bg=False):
    """Load image from assets/ folder, scale if size given.
    size: target (width, height) — scales keeping aspect ratio, then crops/pads.
    remove_white_bg: set True to make white/near-white pixels transparent."""
    path = os.path.join(ASSETS, name)
    img  = pygame.image.load(path).convert_alpha()
    if size:
        # Scale to exact size (stretch to fit) — same as original behavior
        img = pygame.transform.scale(img, size)
    if remove_white_bg:
        # Make all near-white pixels transparent using set_colorkey
        img = img.convert_alpha()
        # Set white as transparent color
        img.set_colorkey((255, 255, 255))
        # Also handle near-white by iterating edge pixels
        w, h = img.get_size()
        for x in range(w):
            for y in range(h):
                r, g, b, a = img.get_at((x, y))
                if r > 230 and g > 230 and b > 230:
                    img.set_at((x, y), (r, g, b, 0))
    return img

# ============================================================
#  Colors
# ============================================================
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
RED     = (220,  50,  50)
GREEN   = ( 50, 200,  50)
BLUE    = ( 50, 120, 220)
YELLOW  = (255, 200,   0)
ORANGE  = (255, 140,   0)
GRAY    = (160, 160, 160)
DARK    = ( 20,  20,  30)
ROAD_C  = ( 60,  60,  70)
LANE_C  = (200, 200,  50)
OIL_C   = ( 20,  20,  80)
NITRO_C = (  0, 230, 255)
SHIELD_C= ( 80, 200, 255)
REPAIR_C= ( 50, 220,  80)

CAR_COLORS = {
    "RED":    (220,  50,  50),
    "BLUE":   ( 50, 120, 220),
    "GREEN":  ( 50, 200,  80),
    "YELLOW": (230, 200,   0),
}

DIFFICULTY_CFG = {
    "Easy":   {"base_speed": 4,  "spawn_interval": 2000, "obstacle_interval": 3000},
    "Normal": {"base_speed": 5,  "spawn_interval": 1500, "obstacle_interval": 2000},
    "Hard":   {"base_speed": 7,  "spawn_interval": 900,  "obstacle_interval": 1200},
}

SCREEN_W = 400
SCREEN_H = 600

# Lane X positions (3 lanes)
LANES = [80, 200, 320]

# Images loaded once at module level (after pygame.init() is called in main.py)
_images = {}

def load_assets():
    """Load all images from assets/ folder. Call once after pygame.init()."""
    _images["background"]    = load_img("AnimatedStreet.png")
    _images["enemy"]         = load_img("Enemy.png")
    _images["coin"]          = load_img("coin.png", (32, 32))
    # Player car per color — all scaled to same size as Player.png
    base = load_img("Player.png")
    CAR_SIZE = base.get_size()   # Use original Player.png size as standard
    _images["player_BLUE"] = base
    for color, filename, rm_white, rotate in [
            ("GREEN",  "Playergreen.png",  True,    0),
            ("YELLOW", "YellowCar.png",    False,  90),
            ("RED",    "Enemy.png",        False, 180)]:
        try:
            raw = load_img(filename, remove_white_bg=rm_white)
            if rotate:
                raw = pygame.transform.rotate(raw, rotate)
            img = pygame.transform.scale(raw, CAR_SIZE)
            _images[f"player_{color}"] = img
        except Exception:
            _images[f"player_{color}"] = _images["player_BLUE"]


# ============================================================
#  Coin class (from Practice 11 — weighted coins)
# ============================================================
COIN_TYPES = [
    {"weight": 1, "color": (205, 127,  50), "label": "+1"},
    {"weight": 3, "color": (192, 192, 192), "label": "+3"},
    {"weight": 5, "color": (255, 215,   0), "label": "+5"},
]
COIN_WEIGHTS = [60, 30, 10]


class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        ct          = random.choices(COIN_TYPES, weights=COIN_WEIGHTS, k=1)[0]
        self.weight = ct["weight"]
        self.color  = ct["color"]
        self.label  = ct["label"]
        # Use coin image from assets as is
        self.image  = _images["coin"].copy()
        self.rect   = self.image.get_rect()
        self.rect.center = (random.choice(LANES), -20)
        self.speed  = speed

    def move(self):
        self.rect.y += self.speed
    def is_off(self): return self.rect.top > SCREEN_H


# ============================================================
#  Enemy car
# ============================================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = _images["enemy"]
        self.rect  = self.image.get_rect()
        self.rect.center = (random.choice(LANES), -80)
        self.speed = speed

    def move(self):
        self.rect.y += self.speed
    def is_off(self): return self.rect.top > SCREEN_H


# ============================================================
#  Road obstacle (oil spill / pothole / barrier)
# ============================================================
OBS_TYPES = [
    {"name": "oil",     "color": OIL_C,           "w": 50, "h": 30, "effect": "slow"},
    {"name": "pothole", "color": (80,  60,  40),   "w": 35, "h": 35, "effect": "slow"},
    {"name": "barrier", "color": (220, 100,   0),  "w": 60, "h": 20, "effect": "crash"},
]


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        ot = random.choice(OBS_TYPES)
        self.effect = ot["effect"]
        self.name   = ot["name"]
        self.image  = pygame.Surface((ot["w"], ot["h"]), pygame.SRCALPHA)
        self.image.fill(ot["color"])
        if ot["name"] == "barrier":
            pygame.draw.rect(self.image, WHITE, (0, 8, ot["w"], 4))
        self.rect   = self.image.get_rect()
        self.rect.center = (random.choice(LANES), -40)
        self.speed  = speed

    def move(self):
        self.rect.y += self.speed
    def is_off(self): return self.rect.top > SCREEN_H


# ============================================================
#  Power-up
# ============================================================
POWERUP_TYPES = [
    {"name": "Nitro",  "color": NITRO_C,  "duration": 4},
    {"name": "Shield", "color": SHIELD_C, "duration": 0},  # until hit
    {"name": "Repair", "color": REPAIR_C, "duration": 0},  # instant
]


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        pt          = random.choice(POWERUP_TYPES)
        self.name   = pt["name"]
        self.color  = pt["color"]
        self.duration = pt["duration"]
        self.image  = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (18, 18), 18)
        font = pygame.font.SysFont("Verdana", 11, bold=True)
        lbl  = font.render(self.name[:3], True, BLACK)
        self.image.blit(lbl, lbl.get_rect(center=(18, 18)))
        self.rect   = self.image.get_rect()
        self.rect.center = (random.choice(LANES), -40)
        self.speed  = speed
        self.spawn_time = pygame.time.get_ticks()

    def move(self):
        self.rect.y += self.speed
    def is_off(self):
        return self.rect.top > SCREEN_H or (pygame.time.get_ticks() - self.spawn_time > 7000)


# ============================================================
#  Nitro boost strip (road event)
# ============================================================
class NitroStrip(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((SCREEN_W, 18), pygame.SRCALPHA)
        self.image.fill((0, 200, 255, 120))
        for x in range(0, SCREEN_W, 30):
            pygame.draw.line(self.image, WHITE, (x, 0), (x + 15, 18), 2)
        self.rect  = self.image.get_rect()
        self.rect.topleft = (0, -20)
        self.speed = speed

    def move(self):
        self.rect.y += self.speed
    def is_off(self): return self.rect.top > SCREEN_H


# ============================================================
#  Player
# ============================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, car_color_name):
        super().__init__()
        # Load the car image matching the selected color from settings
        key = f"player_{car_color_name}"
        self.image = _images.get(key, _images["player_BLUE"]).copy()
        self.rect  = self.image.get_rect()
        self.rect.center = (SCREEN_W // 2, 500)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and self.rect.left  > 40:  self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_W - 40: self.rect.x += 5


# ============================================================
#  Main game function
#  Returns: (score, distance, coins)
# ============================================================
def run_game(screen, clock, username):
    settings   = load_settings()
    cfg        = DIFFICULTY_CFG[settings["difficulty"]]
    car_color  = settings["car_color"]

    # Load assets fresh each run so car color is applied correctly
    load_assets()

    # Load crash sound if available
    crash_sound = None
    try:
        crash_sound = pygame.mixer.Sound(os.path.join(ASSETS, "crash.wav"))
    except Exception:
        pass

    # Background music
    try:
        pygame.mixer.music.load(os.path.join(ASSETS, "background.wav"))
        if settings.get("sound", True):
            pygame.mixer.music.play(-1)
    except Exception:
        pass

    SPEED      = cfg["base_speed"]
    font_small = pygame.font.SysFont("Verdana", 18)
    font_tiny  = pygame.font.SysFont("Verdana", 13)

    player  = Player(car_color)
    road_y  = 0   # Road scroll offset

    # Sprite groups
    enemies_grp   = pygame.sprite.Group()
    coins_grp     = pygame.sprite.Group()
    obstacles_grp = pygame.sprite.Group()
    powerups_grp  = pygame.sprite.Group()
    events_grp    = pygame.sprite.Group()
    all_sprites   = pygame.sprite.Group()
    all_sprites.add(player)

    # Score tracking
    SCORE    = 0
    COINS    = 0
    distance = 0.0   # meters

    # Practice 11: enemy speed boost every N coins
    COIN_THRESHOLD = 5
    next_boost     = COIN_THRESHOLD

    # Power-up state
    active_powerup      = None
    powerup_end_time    = 0
    has_shield          = False
    nitro_active        = False

    # Slow-down effect from oil/pothole
    slow_timer = 0

    # Timers using pygame user events
    SPAWN_ENEMY    = pygame.USEREVENT + 1
    SPAWN_COIN     = pygame.USEREVENT + 2
    SPAWN_OBSTACLE = pygame.USEREVENT + 3
    SPAWN_POWERUP  = pygame.USEREVENT + 4
    SPAWN_EVENT    = pygame.USEREVENT + 5   # Road events (nitro strip)

    pygame.time.set_timer(SPAWN_ENEMY,    cfg["spawn_interval"])
    pygame.time.set_timer(SPAWN_COIN,     1500)
    pygame.time.set_timer(SPAWN_OBSTACLE, cfg["obstacle_interval"])
    pygame.time.set_timer(SPAWN_POWERUP,  5000)
    pygame.time.set_timer(SPAWN_EVENT,    8000)

    running = True

    while running:
        # ---- Current effective speed ----
        eff_speed = SPEED
        if nitro_active:
            eff_speed = int(SPEED * 1.8)
        elif slow_timer > 0:
            eff_speed = max(2, SPEED - 2)
            slow_timer -= 1

        # ---- Events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

            if event.type == SPAWN_ENEMY:
                e = Enemy(eff_speed)
                # Safe spawn: don't overlap player
                if abs(e.rect.centerx - player.rect.centerx) > 40 or e.rect.centery < player.rect.centery - 200:
                    enemies_grp.add(e); all_sprites.add(e)

            if event.type == SPAWN_COIN:
                c = Coin(eff_speed)
                coins_grp.add(c); all_sprites.add(c)

            if event.type == SPAWN_OBSTACLE:
                o = Obstacle(eff_speed)
                obstacles_grp.add(o); all_sprites.add(o)

            if event.type == SPAWN_POWERUP:
                p = PowerUp(eff_speed)
                powerups_grp.add(p); all_sprites.add(p)

            if event.type == SPAWN_EVENT:
                ns = NitroStrip(eff_speed)
                events_grp.add(ns); all_sprites.add(ns)

        # ---- Update ----
        player.move()
        distance += eff_speed * 0.05   # Approximate meters

        for s in list(all_sprites):
            if s != player and hasattr(s, "move"):
                s.move()

        # Remove off-screen sprites
        for grp in [enemies_grp, coins_grp, obstacles_grp, powerups_grp, events_grp]:
            for s in list(grp):
                if s.is_off():
                    s.kill()

        # Check nitro timer
        if nitro_active and pygame.time.get_ticks() > powerup_end_time:
            nitro_active   = False
            active_powerup = None

        # ---- Coin collection ----
        collected = pygame.sprite.spritecollide(player, coins_grp, True)
        for coin in collected:
            COINS += coin.weight
            SCORE += coin.weight * 10

        # Practice 11: speed boost per N coins
        while COINS >= next_boost:
            SPEED     += 1
            next_boost += COIN_THRESHOLD

        # ---- Power-up collection ----
        hit_pu = pygame.sprite.spritecollide(player, powerups_grp, True)
        for pu in hit_pu:
            active_powerup = pu.name
            if pu.name == "Nitro":
                nitro_active    = True
                powerup_end_time = pygame.time.get_ticks() + pu.duration * 1000
            elif pu.name == "Shield":
                has_shield = True
            elif pu.name == "Repair":
                # Instant: clear one obstacle nearest to player
                obs_list = sorted(list(obstacles_grp),
                                  key=lambda o: abs(o.rect.centery - player.rect.centery))
                if obs_list:
                    obs_list[0].kill()
                active_powerup = None

        # ---- Nitro strip road event ----
        hit_event = pygame.sprite.spritecollide(player, events_grp, True)
        for ev in hit_event:
            nitro_active    = True
            active_powerup  = "Nitro"
            powerup_end_time = pygame.time.get_ticks() + 3000

        # ---- Obstacle collision ----
        hit_obs = pygame.sprite.spritecollide(player, obstacles_grp, False)
        for obs in hit_obs:
            if obs.effect == "crash":
                if has_shield:
                    has_shield = False
                    active_powerup = None
                    obs.kill()
                else:
                    return SCORE, distance, COINS   # Game over
            elif obs.effect == "slow":
                slow_timer = 60   # Slow for 60 frames (~1 sec)
                obs.kill()

        # ---- Enemy collision ----
        if pygame.sprite.spritecollideany(player, enemies_grp):
            if has_shield:
                has_shield = False
                active_powerup = None
                for e in list(enemies_grp):
                    if pygame.sprite.collide_rect(player, e):
                        e.kill()
                        break
            else:
                if crash_sound and settings.get("sound", True):
                    crash_sound.play()
                pygame.mixer.music.stop()
                return SCORE, distance, COINS

        # ---- Difficulty scaling: increase spawn rate over time ----
        if int(distance) % 200 == 0 and int(distance) > 0:
            interval = max(400, cfg["spawn_interval"] - int(distance) // 5)
            pygame.time.set_timer(SPAWN_ENEMY, interval)

        # ---- Draw ----
        # Scrolling background from assets/AnimatedStreet.png
        bg = _images["background"]
        road_y = (road_y + eff_speed) % SCREEN_H
        screen.blit(bg, (0, road_y - SCREEN_H))
        screen.blit(bg, (0, road_y))

        # Draw all sprites
        for entity in all_sprites:
            screen.blit(entity.image, entity.rect)

        # Shield ring around player
        if has_shield:
            pygame.draw.circle(screen, SHIELD_C,
                               player.rect.center, 38, 3)

        # ---- HUD ----
        screen.blit(font_small.render(f"Score: {SCORE}", True, WHITE), (8, 8))
        screen.blit(font_small.render(f"Coins: {COINS}", True, YELLOW), (8, 30))
        screen.blit(font_small.render(f"Dist:  {int(distance)}m", True, GRAY), (8, 52))

        # Active power-up display
        if active_powerup:
            if nitro_active:
                remain = max(0, (powerup_end_time - pygame.time.get_ticks()) // 1000)
                pu_text = f"⚡ NITRO {remain}s"
                pu_color = NITRO_C
            elif has_shield:
                pu_text  = "🛡 SHIELD"
                pu_color = SHIELD_C
            else:
                pu_text  = active_powerup
                pu_color = WHITE
            pu_surf = font_small.render(pu_text, True, pu_color)
            screen.blit(pu_surf, (SCREEN_W - pu_surf.get_width() - 8, 8))

        # Slow indicator
        if slow_timer > 0:
            sl = font_tiny.render("SLOW!", True, OIL_C)
            screen.blit(sl, (SCREEN_W - sl.get_width() - 8, 32))

        pygame.display.flip()
        clock.tick(60)

    return SCORE, distance, COINS
