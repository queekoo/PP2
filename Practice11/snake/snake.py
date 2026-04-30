import pygame
import random

pygame.init()

# --- SETTINGS ---
WIDTH = 600
HEIGHT = 600
CELL = 30

COLS = WIDTH // CELL   # Number of columns in the grid
ROWS = HEIGHT // CELL  # Number of rows in the grid

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()
font      = pygame.font.SysFont(None, 36)
font_tiny = pygame.font.SysFont(None, 22)  # Smaller font for food labels and timer

# --- COLORS ---
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0  )
RED    = (255, 0,   0  )
GREEN  = (0,   200, 0  )   # Regular food color (weight 1)
YELLOW = (255, 255, 0  )   # Snake body color
ORANGE = (255, 165, 0  )   # Medium food color (weight 2)
PURPLE = (180, 0,   255)   # Rare food color (weight 3)
GRAY   = (160, 160, 160)   # Used for disappearing timer bar


# ============================================================
#  Extra Task #1 — Food type configuration
#  Each food type has a weight (points), color, label, and
#  a lifetime in milliseconds (how long before it disappears).
#  Rarer/higher-weight foods disappear faster.
# ============================================================
FOOD_TYPES = [
    {"weight": 1, "color": GREEN,  "label": "+1", "lifetime": 8000},  # Common  — 8 sec
    {"weight": 2, "color": ORANGE, "label": "+2", "lifetime": 5000},  # Medium  — 5 sec
    {"weight": 3, "color": PURPLE, "label": "+3", "lifetime": 3000},  # Rare    — 3 sec
]

# Weighted spawn probability: green 60%, orange 30%, purple 10%
FOOD_SPAWN_WEIGHTS = [60, 30, 10]


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# ============================================================
#  Snake Class — handles movement, drawing, and food eating
# ============================================================
class Snake:
    def __init__(self):
        # Start with 3 body segments moving right
        self.body  = [Point(10, 10), Point(9, 10), Point(8, 10)]
        self.dx    = 1    # Horizontal direction (1 = right, -1 = left, 0 = none)
        self.dy    = 0    # Vertical direction   (1 = down,  -1 = up,   0 = none)
        self.score = 0
        self.level = 1
        self.alive = True

    def move(self):
        # Shift every body segment forward (from tail to neck) to follow the head
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        # Move the head in the current direction
        self.body[0].x += self.dx
        self.body[0].y += self.dy

        # --- Wall collision: die if the head goes out of bounds ---
        if (self.body[0].x < 0 or self.body[0].x >= COLS or
                self.body[0].y < 1 or self.body[0].y >= ROWS):
            self.alive = False

        # --- Self collision: die if the head hits any body segment ---
        head = self.body[0]
        for s in self.body[1:]:
            if head.x == s.x and head.y == s.y:
                self.alive = False

    def draw(self):
        # Draw the head in red
        head = self.body[0]
        pygame.draw.rect(screen, RED, (head.x * CELL, head.y * CELL, CELL, CELL))

        # Draw the rest of the body in yellow
        for s in self.body[1:]:
            pygame.draw.rect(screen, YELLOW, (s.x * CELL, s.y * CELL, CELL, CELL))

    def check_food(self, food_list):
        """
        Check if the snake's head overlaps with any food item.
        If so, eat it: add its weight to the score, grow the snake,
        remove the eaten food from the list, and update the level.
        Returns a list of food items that were eaten (so caller can respawn).
        """
        head = self.body[0]
        eaten = []

        for food in food_list:
            if head.x == food.x and head.y == food.y:
                self.score += food.weight  # Extra Task #1: add weight, not just 1
                # Grow the snake by appending a new segment at the tail position
                self.body.append(Point(self.body[-1].x, self.body[-1].y))
                eaten.append(food)

        # Level up every 3 points scored
        self.level = 1 + self.score // 3
        return eaten


# ============================================================
#  Food Class — Extra Task #1 & #2
#  Each food has a random weight (points), a color, and a
#  lifetime timer. It disappears when the timer runs out.
# ============================================================
class Food:
    def __init__(self, snake_body):
        # --- Randomly pick a food type based on weighted probability ---
        food_type     = random.choices(FOOD_TYPES, weights=FOOD_SPAWN_WEIGHTS, k=1)[0]
        self.weight   = food_type["weight"]    # Point value when eaten
        self.color    = food_type["color"]     # Display color
        self.label    = food_type["label"]     # Text shown above the food (e.g. "+2")
        self.lifetime = food_type["lifetime"]  # How long (ms) before it disappears

        # Record the time this food was spawned (used to compute remaining time)
        self.spawn_time = pygame.time.get_ticks()

        # Place the food at a random position that doesn't overlap the snake
        self.x, self.y = self._random_position(snake_body)

    def _random_position(self, snake_body):
        """Find a grid cell that is not currently occupied by the snake."""
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(1, ROWS - 1)  # Row 0 is the HUD bar — keep food below it
            if not any(x == s.x and y == s.y for s in snake_body):
                return x, y

    def is_expired(self):
        """Return True if this food has been on screen longer than its lifetime."""
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return elapsed >= self.lifetime

    def remaining_ratio(self):
        """Return a 0.0–1.0 value representing how much lifetime is left (1.0 = just spawned)."""
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0.0, 1.0 - elapsed / self.lifetime)

    def draw(self):
        """Draw the food square, its weight label, and a countdown bar below it."""
        px = self.x * CELL
        py = self.y * CELL

        # Draw the colored food square
        pygame.draw.rect(screen, self.color, (px, py, CELL, CELL))

        # --- Draw the weight label centered above the food ---
        label_surf = font_tiny.render(self.label, True, WHITE)
        lx = px + (CELL - label_surf.get_width()) // 2
        ly = py - label_surf.get_height()          # Just above the food tile
        screen.blit(label_surf, (lx, ly))

        # --- Draw a timer bar below the food (Extra Task #2) ---
        # The bar shrinks from full width to zero as the lifetime runs out.
        bar_width  = int(CELL * self.remaining_ratio())  # Current bar width in pixels
        bar_height = 4                                    # Bar is 4 pixels tall
        bar_y      = py + CELL + 1                       # Just below the food tile

        # Gray background (full width) so the shrinking bar is easy to see
        pygame.draw.rect(screen, GRAY, (px, bar_y, CELL, bar_height))
        # Colored foreground (shrinking)
        if bar_width > 0:
            pygame.draw.rect(screen, self.color, (px, bar_y, bar_width, bar_height))


# ============================================================
#  INIT
# ============================================================
snake      = Snake()
food_list  = []   # List of all active Food objects on screen

# Spawn the first food item to get the game started
food_list.append(Food(snake.body))

FPS     = 5
running = True

# Timer: spawn a new food item every 3 seconds regardless of eating
SPAWN_FOOD_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_FOOD_EVENT, 3000)  # Every 3000ms = 3 seconds

# Maximum number of food items allowed on screen at once
MAX_FOOD = 5


# ============================================================
#  MAIN LOOP
# ============================================================
while running:

    # --- Game Over screen ---
    if not snake.alive:
        screen.fill(BLACK)
        text1 = font.render("GAME OVER", True, RED)
        text2 = font.render(f"Score: {snake.score}  Level: {snake.level}", True, WHITE)
        screen.blit(text1, (200, 250))
        screen.blit(text2, (130, 300))
        pygame.display.flip()
        pygame.time.wait(3000)
        break

    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Arrow key input — prevent the snake from reversing on itself
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and snake.dx != -1:
                snake.dx, snake.dy = 1, 0
            elif event.key == pygame.K_LEFT and snake.dx != 1:
                snake.dx, snake.dy = -1, 0
            elif event.key == pygame.K_DOWN and snake.dy != -1:
                snake.dx, snake.dy = 0, 1
            elif event.key == pygame.K_UP and snake.dy != 1:
                snake.dx, snake.dy = 0, -1

        # Extra Task #2: Spawn a new food item on the timed event
        if event.type == SPAWN_FOOD_EVENT:
            if len(food_list) < MAX_FOOD:  # Don't exceed the maximum food count
                food_list.append(Food(snake.body))

    # --- Update snake position ---
    snake.move()

    # --- Check which foods the snake ate ---
    eaten = snake.check_food(food_list)
    # Remove eaten foods from the list
    for f in eaten:
        food_list.remove(f)

    # --- Extra Task #2: Remove expired food items (they disappear after their timer) ---
    food_list = [f for f in food_list if not f.is_expired()]

    # --- Make sure there is always at least one food item on screen ---
    if len(food_list) == 0:
        food_list.append(Food(snake.body))

    # --- Draw everything ---
    screen.fill(BLACK)

    # HUD — score and level displayed at the top
    score_text = font.render(f"Score: {snake.score}", True, WHITE)
    level_text = font.render(f"Level: {snake.level}", True, WHITE)
    screen.blit(score_text, (10, 5))
    screen.blit(level_text, (200, 5))

    # Draw the snake
    snake.draw()

    # Draw all active food items (each draws itself + timer bar)
    for food in food_list:
        food.draw()

    pygame.display.flip()

    # Speed increases with level — higher level = faster snake
    clock.tick(6 + snake.level)

pygame.quit()
