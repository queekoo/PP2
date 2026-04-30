import pygame
import random

pygame.init()

# --- SETTINGS ---
WIDTH = 600
HEIGHT = 600
CELL = 30

COLS = WIDTH // CELL
ROWS = HEIGHT // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# --- COLORS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# SNAKE
2
class Snake:
    def __init__(self):
        self.body = [Point(10, 10), Point(9, 10), Point(8, 10)]
        self.dx = 1
        self.dy = 0
        self.score = 0
        self.level = 1
        self.alive = True

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        self.body[0].x += self.dx
        self.body[0].y += self.dy

        # --- WALL COLLISION ---
        if (self.body[0].x < 0 or self.body[0].x >= COLS or
            self.body[0].y < 1 or self.body[0].y >= ROWS):
            self.alive = False

        # --- SELF COLLISION ---
        head = self.body[0]
        for s in self.body[1:]:
            if head.x == s.x and head.y == s.y:
                self.alive = False

    def draw(self):
        head = self.body[0]
        pygame.draw.rect(screen, RED, (head.x * CELL, head.y * CELL, CELL, CELL))

        for s in self.body[1:]:
            pygame.draw.rect(screen, YELLOW, (s.x * CELL, s.y * CELL, CELL, CELL))

    def check_food(self, food):
        head = self.body[0]
        if head.x == food.x and head.y == food.y:
            self.score += 1
            self.body.append(Point(head.x, head.y))
            food.spawn(self.body)
            self.level = 1 + self.score // 3

# ============================================================
# FOOD
# ============================================================
class Food:
    def __init__(self):
        self.x = 0
        self.y = 0

    def spawn(self, snake_body):
        while True:
            self.x = random.randint(0, COLS - 1)
            self.y = random.randint(1, ROWS - 1)  # не в верхней строке
            if not any(self.x == s.x and self.y == s.y for s in snake_body):
                break

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x * CELL, self.y * CELL, CELL, CELL))

# ============================================================
# INIT
# ============================================================
snake = Snake()
food = Food()
food.spawn(snake.body)

FPS = 5
running = True

# ============================================================
# LOOP
# ============================================================
while running:

    if not snake.alive:
        screen.fill(BLACK)
        text1 = font.render("GAME OVER", True, RED)
        text2 = font.render(f"Score: {snake.score} Level: {snake.level}", True, WHITE)
        screen.blit(text1, (200, 250))
        screen.blit(text2, (150, 300))
        pygame.display.flip()
        pygame.time.wait(3000)
        break

    # --- EVENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and snake.dx != -1:
                snake.dx, snake.dy = 1, 0
            elif event.key == pygame.K_LEFT and snake.dx != 1:
                snake.dx, snake.dy = -1, 0
            elif event.key == pygame.K_DOWN and snake.dy != -1:
                snake.dx, snake.dy = 0, 1
            elif event.key == pygame.K_UP and snake.dy != 1:
                snake.dx, snake.dy = 0, -1

    snake.move()
    snake.check_food(food)

    screen.fill(BLACK)

    # UI
    score_text = font.render(f"Score: {snake.score}", True, WHITE)
    level_text = font.render(f"Level: {snake.level}", True, WHITE)
    screen.blit(score_text, (10, 5))
    screen.blit(level_text, (150, 5))

    snake.draw()
    food.draw()

    pygame.display.flip()
    clock.tick(6 + snake.level)

pygame.quit()