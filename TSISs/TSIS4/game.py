import pygame
import random
import json
import os

# ============================================================
#  Constants
# ============================================================
WIDTH  = 600
HEIGHT = 640   # Extra 40px for HUD at top
CELL   = 30
COLS   = WIDTH  // CELL
ROWS   = (HEIGHT - 40) // CELL   # Playfield rows (below HUD)
HUD_H  = 40    # Height of the top HUD bar

SETTINGS_FILE = "settings.json"

# ============================================================
#  Colors
# ============================================================
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (180, 180, 180)
DARK_GRAY  = ( 40,  40,  40)
RED        = (220,  50,  50)
DARK_RED   = (120,  10,  10)   # Poison food
GREEN      = (  0, 200,   0)
YELLOW     = (255, 220,   0)
ORANGE     = (255, 140,   0)
BLUE       = ( 50, 120, 220)
CYAN       = (  0, 210, 210)
PURPLE     = (160,  50, 220)
BROWN      = (139,  90,  43)
GRID_COLOR = ( 50,  50,  50)

# Food types (from Practice 11)
FOOD_TYPES = [
    {"weight": 1, "color": GREEN,  "label": "+1", "lifetime": 8000},
    {"weight": 2, "color": ORANGE, "label": "+2", "lifetime": 5000},
    {"weight": 3, "color": YELLOW, "label": "+3", "lifetime": 3000},
]
FOOD_SPAWN_WEIGHTS = [60, 30, 10]

# Power-up types
POWERUP_TYPES = [
    {"name": "Speed",  "color": CYAN,   "label": "⚡"},
    {"name": "Slow",   "color": BLUE,   "label": "🐢"},
    {"name": "Shield", "color": PURPLE, "label": "🛡"},
]


# ============================================================
#  Settings helpers
# ============================================================
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"snake_color": [0, 200, 0], "grid": True, "sound": True}


def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)


# ============================================================
#  Point helper
# ============================================================
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# ============================================================
#  Food
# ============================================================
class Food:
    def __init__(self, blocked):
        ft = random.choices(FOOD_TYPES, weights=FOOD_SPAWN_WEIGHTS, k=1)[0]
        self.weight     = ft["weight"]
        self.color      = ft["color"]
        self.label      = ft["label"]
        self.lifetime   = ft["lifetime"]
        self.spawn_time = pygame.time.get_ticks()
        self.x, self.y  = self._place(blocked)

    def _place(self, blocked):
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)
            if (x, y) not in blocked:
                return x, y

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= self.lifetime

    def remaining_ratio(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0.0, 1.0 - elapsed / self.lifetime)

    def draw(self, surface, font_tiny):
        px, py = self.x * CELL, HUD_H + self.y * CELL
        pygame.draw.rect(surface, self.color, (px, py, CELL, CELL))
        lbl = font_tiny.render(self.label, True, BLACK)
        surface.blit(lbl, (px + (CELL - lbl.get_width()) // 2, py - lbl.get_height()))
        # Timer bar
        bw = int(CELL * self.remaining_ratio())
        pygame.draw.rect(surface, GRAY,       (px, py + CELL + 1, CELL, 3))
        if bw > 0:
            pygame.draw.rect(surface, self.color, (px, py + CELL + 1, bw,   3))


# ============================================================
#  Poison Food
# ============================================================
class PoisonFood:
    def __init__(self, blocked):
        self.color      = DARK_RED
        self.lifetime   = 6000
        self.spawn_time = pygame.time.get_ticks()
        self.x, self.y  = self._place(blocked)

    def _place(self, blocked):
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)
            if (x, y) not in blocked:
                return x, y

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= self.lifetime

    def draw(self, surface, font_tiny):
        px, py = self.x * CELL, HUD_H + self.y * CELL
        pygame.draw.rect(surface, self.color, (px, py, CELL, CELL))
        # Skull indicator
        lbl = font_tiny.render("☠", True, RED)
        surface.blit(lbl, (px + (CELL - lbl.get_width()) // 2, py + 2))


# ============================================================
#  Power-up
# ============================================================
class PowerUp:
    def __init__(self, blocked):
        pt = random.choice(POWERUP_TYPES)
        self.name       = pt["name"]
        self.color      = pt["color"]
        self.label      = pt["label"]
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime   = 8000   # Disappears after 8 sec if not collected
        self.x, self.y  = self._place(blocked)

    def _place(self, blocked):
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)
            if (x, y) not in blocked:
                return x, y

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= self.lifetime

    def draw(self, surface, font_tiny):
        px, py = self.x * CELL, HUD_H + self.y * CELL
        pygame.draw.circle(surface, self.color, (px + CELL//2, py + CELL//2), CELL//2 - 2)
        lbl = font_tiny.render(self.name[:3], True, WHITE)
        surface.blit(lbl, (px + (CELL - lbl.get_width()) // 2, py + (CELL - lbl.get_height()) // 2))


# ============================================================
#  Snake
# ============================================================
class Snake:
    def __init__(self, color):
        self.body  = [Point(10, 8), Point(9, 8), Point(8, 8)]
        self.dx    = 1
        self.dy    = 0
        self.alive = True
        self.color = color
        self.head_color = tuple(min(255, c + 60) for c in color)

    def move(self, obstacles, shield_active):
        # Shift body
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        self.body[0].x += self.dx
        self.body[0].y += self.dy

        hx, hy = self.body[0].x, self.body[0].y

        # Wall collision
        if hx < 0 or hx >= COLS or hy < 0 or hy >= ROWS:
            if shield_active:
                # Wrap around instead of dying
                self.body[0].x = hx % COLS
                self.body[0].y = hy % ROWS
                return True   # Shield used
            else:
                self.alive = False

        # Self collision
        for seg in self.body[1:]:
            if hx == seg.x and hy == seg.y:
                if shield_active:
                    return True   # Shield used
                self.alive = False

        # Obstacle collision
        if (hx, hy) in obstacles:
            if shield_active:
                return True
            self.alive = False

        return False   # Shield not triggered

    def draw(self, surface):
        for i, seg in enumerate(self.body):
            px = seg.x * CELL
            py = HUD_H + seg.y * CELL
            color = self.head_color if i == 0 else self.color
            pygame.draw.rect(surface, color, (px + 1, py + 1, CELL - 2, CELL - 2),
                             border_radius=4)


# ============================================================
#  Obstacle block set
# ============================================================
def generate_obstacles(level, snake_body):
    """Place wall blocks for levels >= 3. Avoid trapping the snake."""
    if level < 3:
        return set()

    occupied = {(s.x, s.y) for s in snake_body}
    count    = min(4 + (level - 3) * 2, 20)   # More blocks at higher levels
    blocks   = set()

    attempts = 0
    while len(blocks) < count and attempts < 500:
        attempts += 1
        x = random.randint(1, COLS - 2)
        y = random.randint(1, ROWS - 2)
        if (x, y) not in occupied and (x, y) not in blocks:
            # Don't place adjacent to snake head (safety buffer)
            hx, hy = snake_body[0].x, snake_body[0].y
            if abs(x - hx) > 2 or abs(y - hy) > 2:
                blocks.add((x, y))

    return blocks


# ============================================================
#  Main game loop
#  Returns: (score, level)
# ============================================================
def run_game(screen, clock, username, personal_best):
    settings     = load_settings()
    snake_color  = tuple(settings["snake_color"])
    show_grid    = settings["grid"]

    font       = pygame.font.SysFont("Verdana", 20)
    font_small = pygame.font.SysFont("Verdana", 16)
    font_tiny  = pygame.font.SysFont("Verdana", 12)

    # Load and play background music
    if settings.get("sound", True):
        try:
            pygame.mixer.music.load(os.path.join("assets", "backgound-sound.wav"))
            pygame.mixer.music.play(-1)   # Loop forever
        except Exception:
            pass

    # Load game over sound
    gameover_sound = None
    if settings.get("sound", True):
        try:
            gameover_sound = pygame.mixer.Sound(os.path.join("assets", "game-over.wav"))
        except Exception:
            pass

    snake      = Snake(snake_color)
    score      = 0
    level      = 1
    obstacles  = set()

    food_list  = []
    poison     = None
    powerup    = None   # At most one power-up on field

    # Active power-up effect
    active_effect    = None   # "Speed", "Slow", "Shield"
    effect_end_time  = 0
    shield_active    = False

    # Timers
    SPAWN_FOOD    = pygame.USEREVENT + 1
    SPAWN_POISON  = pygame.USEREVENT + 2
    SPAWN_POWERUP = pygame.USEREVENT + 3

    pygame.time.set_timer(SPAWN_FOOD,    3000)
    pygame.time.set_timer(SPAWN_POISON,  7000)
    pygame.time.set_timer(SPAWN_POWERUP, 10000)

    def blocked_cells():
        cells = {(s.x, s.y) for s in snake.body} | obstacles
        for f in food_list: cells.add((f.x, f.y))
        if poison:   cells.add((poison.x, poison.y))
        if powerup:  cells.add((powerup.x, powerup.y))
        return cells

    # Spawn initial food
    food_list.append(Food(blocked_cells()))

    base_fps = 6
    running  = True

    while running:
        # ---- Effective FPS ----
        now = pygame.time.get_ticks()
        if active_effect == "Speed" and now < effect_end_time:
            fps = base_fps + 4
        elif active_effect == "Slow" and now < effect_end_time:
            fps = max(2, base_fps - 3)
        else:
            if active_effect in ("Speed", "Slow") and now >= effect_end_time:
                active_effect = None
            fps = base_fps

        # ---- Events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and snake.dx != -1:
                    snake.dx, snake.dy = 1, 0
                elif event.key == pygame.K_LEFT and snake.dx != 1:
                    snake.dx, snake.dy = -1, 0
                elif event.key == pygame.K_DOWN and snake.dy != -1:
                    snake.dx, snake.dy = 0, 1
                elif event.key == pygame.K_UP and snake.dy != 1:
                    snake.dx, snake.dy = 0, -1

            if event.type == SPAWN_FOOD and len(food_list) < 5:
                food_list.append(Food(blocked_cells()))

            if event.type == SPAWN_POISON and poison is None:
                poison = PoisonFood(blocked_cells())

            if event.type == SPAWN_POWERUP and powerup is None:
                powerup = PowerUp(blocked_cells())

        # ---- Move snake ----
        shield_triggered = snake.move(obstacles, shield_active)
        if shield_triggered:
            shield_active = False
            active_effect = None

        if not snake.alive:
            pygame.mixer.music.stop()
            if gameover_sound:
                gameover_sound.play()
                pygame.time.wait(1500)   # Wait for sound to finish
            return score, level

        hx, hy = snake.body[0].x, snake.body[0].y

        # ---- Eat normal food ----
        for food in list(food_list):
            if hx == food.x and hy == food.y:
                score += food.weight
                snake.body.append(Point(snake.body[-1].x, snake.body[-1].y))
                food_list.remove(food)
                # Level up every 5 points
                new_level = 1 + score // 5
                if new_level > level:
                    level      = new_level
                    base_fps   = 6 + level
                    obstacles  = generate_obstacles(level, snake.body)

        # ---- Eat poison food ----
        if poison and hx == poison.x and hy == poison.y:
            poison = None
            # Shorten snake by 2
            if len(snake.body) <= 3:
                snake.alive = False
                pygame.mixer.music.stop()
                if gameover_sound:
                    gameover_sound.play()
                    pygame.time.wait(1500)
                return score, level
            snake.body = snake.body[:-2]

        # ---- Collect power-up ----
        if powerup and hx == powerup.x and hy == powerup.y:
            active_effect = powerup.name
            if powerup.name == "Shield":
                shield_active   = True
                active_effect   = "Shield"
                effect_end_time = 0   # Shield lasts until triggered
            else:
                effect_end_time = pygame.time.get_ticks() + 5000
            powerup = None

        # ---- Expire items ----
        food_list = [f for f in food_list if not f.is_expired()]
        if poison  and poison.is_expired():  poison  = None
        if powerup and powerup.is_expired(): powerup = None

        # ---- Keep at least 1 food ----
        if not food_list:
            food_list.append(Food(blocked_cells()))

        # ---- Draw ----
        screen.fill(DARK_GRAY)

        # Grid overlay
        if show_grid:
            for gx in range(0, WIDTH, CELL):
                pygame.draw.line(screen, GRID_COLOR, (gx, HUD_H), (gx, HEIGHT))
            for gy in range(HUD_H, HEIGHT, CELL):
                pygame.draw.line(screen, GRID_COLOR, (0, gy), (WIDTH, gy))

        # Obstacles
        for (ox, oy) in obstacles:
            pygame.draw.rect(screen, BROWN,
                             (ox * CELL, HUD_H + oy * CELL, CELL, CELL))
            pygame.draw.rect(screen, BLACK,
                             (ox * CELL, HUD_H + oy * CELL, CELL, CELL), 1)

        # Food, poison, power-up
        for food in food_list:
            food.draw(screen, font_tiny)
        if poison:
            poison.draw(screen, font_tiny)
        if powerup:
            powerup.draw(screen, font_tiny)

        # Snake
        snake.draw(screen)

        # Shield glow around head
        if shield_active:
            hpx = snake.body[0].x * CELL + CELL // 2
            hpy = HUD_H + snake.body[0].y * CELL + CELL // 2
            pygame.draw.circle(screen, PURPLE, (hpx, hpy), CELL, 2)

        # ---- HUD ----
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HUD_H))
        screen.blit(font_small.render(f"Score: {score}", True, WHITE), (8, 10))
        screen.blit(font_small.render(f"Level: {level}", True, WHITE), (140, 10))
        screen.blit(font_small.render(f"Best: {personal_best}", True, YELLOW), (270, 10))

        # Active effect indicator
        if active_effect:
            if active_effect == "Shield":
                eff_txt = "🛡 SHIELD"
                eff_col = PURPLE
            elif active_effect == "Speed":
                remain  = max(0, (effect_end_time - pygame.time.get_ticks()) // 1000)
                eff_txt = f"⚡ SPEED {remain}s"
                eff_col = CYAN
            else:
                remain  = max(0, (effect_end_time - pygame.time.get_ticks()) // 1000)
                eff_txt = f"🐢 SLOW {remain}s"
                eff_col = BLUE
            ef = font_small.render(eff_txt, True, eff_col)
            screen.blit(ef, (WIDTH - ef.get_width() - 8, 10))

        pygame.display.flip()
        clock.tick(fps)

    return score, level
