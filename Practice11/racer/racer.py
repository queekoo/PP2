import pygame, sys
from pygame.locals import *
import random, time


pygame.init()


FPS = 60
FramePerSec = pygame.time.Clock()

# --- Colors ---
BLUE   = (0, 0, 255)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GOLD   = (255, 215, 0)    # Color for gold coins / coin HUD text
SILVER = (192, 192, 192)  # Color for silver coins
BRONZE = (205, 127, 50)   # Color for bronze coins

# --- Game Variables ---
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
SPEED = 5       # Starting speed of the enemy car
SCORE = 0       # Score: increases each time enemy passes the player
COINS = 0       # Total weighted coin value collected by the player

# Extra Task #2: Every N coins collected, the enemy gets faster
COIN_SPEED_THRESHOLD = 5   # Speed up the enemy every 5 coin-points earned
next_speed_up = COIN_SPEED_THRESHOLD  # Tracks the next coin milestone for speed increase

# --- Fonts ---
font       = pygame.font.SysFont("Verdana", 60)   # Large font for "Game Over"
font_small = pygame.font.SysFont("Verdana", 20)   # Small font for score and coins
font_tiny  = pygame.font.SysFont("Verdana", 14)   # Tiny font for coin weight label

# Pre-render the static "Game Over" text (done outside the loop for performance)
game_over_text = font.render("Game Over", True, BLACK)

# --- Create the display window FIRST (required before convert_alpha) ---
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")

# --- Load images from resources folder ---
background = pygame.image.load("resources/AnimatedStreet.png")   # Road background
coin_image = pygame.image.load("resources/coin.png").convert_alpha()  # Coin image
coin_image = pygame.transform.scale(coin_image, (40, 40))        # Resize coin to 40x40 px

# --- Load sounds from resources folder ---
try:
    pygame.mixer.init()
    pygame.mixer.music.load("resources/background.wav")  # Background music
    pygame.mixer.music.play(-1)                           # Play on loop (-1 = forever)
except:
    print("Sound disabled")


# ============================================================
#  Extra Task #1 — Coin weight configuration
#  Each coin type has a (weight, color_tint, label) tuple.
#  The weight is how many coin-points it is worth.
#  We tint the coin image at spawn time to visually distinguish them.
# ============================================================
COIN_TYPES = [
    {"weight": 1, "color": BRONZE, "label": "+1"},  # Bronze coin — most common
    {"weight": 3, "color": SILVER, "label": "+3"},  # Silver coin — uncommon
    {"weight": 5, "color": GOLD,   "label": "+5"},  # Gold coin   — rare
]

# Weighted random selection: bronze appears ~60%, silver ~30%, gold ~10%
COIN_WEIGHTS = [60, 30, 10]


# ============================================================
#  Enemy Class — the car coming from the top
# ============================================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load the enemy car image from resources folder
        self.image = pygame.image.load("resources/Enemy.png")
        # Create a rect matching the image size — used for collision detection
        self.rect = self.image.get_rect()
        # Spawn the enemy at a random horizontal position, just above the screen
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        # Move the enemy downward by SPEED pixels each frame
        self.rect.move_ip(0, SPEED)
        # If the enemy has passed the bottom of the screen, reset it to the top
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1  # Player successfully avoided the enemy: +1 score
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


# ============================================================
#  Player Class — the car controlled by the player
# ============================================================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load the player car image from resources folder
        self.image = pygame.image.load("resources/Player.png")
        # Create a rect matching the image size
        self.rect = self.image.get_rect()
        # Place the player near the bottom center of the screen
        self.rect.center = (160, 520)

    def move(self):
        # Get the state of all keyboard keys
        pressed_keys = pygame.key.get_pressed()

        # Move left — but only if the player is not at the left edge
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)

        # Move right — but only if the player is not at the right edge
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)


# ============================================================
#  Coin Class — Extra Task #1: coins with different weights
#  Each coin is randomly assigned a type (bronze/silver/gold).
#  Heavier coins are rarer (controlled by COIN_WEIGHTS above).
# ============================================================
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # --- Randomly pick a coin type based on weighted probability ---
        coin_type = random.choices(COIN_TYPES, weights=COIN_WEIGHTS, k=1)[0]
        self.weight = coin_type["weight"]   # How many points this coin is worth
        self.label  = coin_type["label"]    # Text shown on the coin (e.g. "+3")
        self.color  = coin_type["color"]    # Tint color for the coin image

        # --- Tint the coin image to match the coin type ---
        # We create a copy so we don't modify the shared coin_image surface
        self.image = coin_image.copy()
        # Create a colored overlay surface (same size as coin, with alpha channel)
        tint_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        # Fill the overlay with the coin's color at 50% opacity (128 out of 255)
        tint_surface.fill((*self.color, 128))
        # Blend the tint onto the coin image using multiplication blending
        self.image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Create a rect for collision detection
        self.rect = self.image.get_rect()
        # Spawn at a random horizontal position just above the screen
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        # Coins fall at the same speed as the enemy car
        self.rect.move_ip(0, SPEED)

    def is_off_screen(self):
        # Returns True if the coin has scrolled past the bottom of the screen
        return self.rect.top > SCREEN_HEIGHT


# ============================================================
#  Sprite Setup
# ============================================================
P1 = Player()
E1 = Enemy()

# Sprite groups make it easy to update and draw many sprites at once
enemies     = pygame.sprite.Group()
enemies.add(E1)

coins_group = pygame.sprite.Group()  # Group for all active coins on screen

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)


# ============================================================
#  User Events
# ============================================================
# Custom event: fires every 1000ms (1 second) to increase game speed
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Custom event: fires every 1500ms to spawn a new coin on the road
SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 1500)


# ============================================================
#  Main Game Loop
# ============================================================
while True:

    # --- Handle all events ---
    for event in pygame.event.get():

        # Increase speed every second — makes the game harder over time
        if event.type == INC_SPEED:
            SPEED += 0.5

        # Spawn a new coin every 1.5 seconds
        if event.type == SPAWN_COIN:
            new_coin = Coin()
            coins_group.add(new_coin)   # Add to the coins group
            all_sprites.add(new_coin)   # Also add to all_sprites so it gets drawn

        # Quit the game when the window is closed
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # --- Draw background first (must be drawn before sprites) ---
    DISPLAYSURF.blit(background, (0, 0))

    # --- Render and display the SCORE in the top-left corner ---
    score_text = font_small.render("Score: " + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(score_text, (10, 10))

    # --- Render and display COINS in the top-right corner ---
    coins_text = font_small.render("Coins: " + str(COINS), True, GOLD)
    DISPLAYSURF.blit(coins_text, (SCREEN_WIDTH - coins_text.get_width() - 10, 10))

    # --- Show next speed-up milestone so player knows how close the enemy boost is ---
    # Extra Task #2: displays "Next boost: X coins" below the coin counter
    boost_text = font_tiny.render("Next boost: " + str(next_speed_up) + " coins", True, RED)
    DISPLAYSURF.blit(boost_text, (SCREEN_WIDTH - boost_text.get_width() - 10, 35))

    # --- Move and redraw all sprites (player, enemy, coins) ---
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # --- Draw the weight label on top of each coin so the player can see its value ---
    for coin in coins_group:
        label_surf = font_tiny.render(coin.label, True, BLACK)
        # Center the label horizontally on the coin
        label_x = coin.rect.centerx - label_surf.get_width() // 2
        label_y = coin.rect.top - label_surf.get_height() - 2  # Just above the coin
        DISPLAYSURF.blit(label_surf, (label_x, label_y))

    # --- Remove coins that have gone off the bottom of the screen ---
    for coin in list(coins_group):
        if coin.is_off_screen():
            coin.kill()  # Remove from all groups

    # --- Check if player collected any coins (collision detection) ---
    # spritecollide returns a list of coins that collided with P1 and removes them (True = dokill)
    collected = pygame.sprite.spritecollide(P1, coins_group, True)
    for coin in collected:
        COINS += coin.weight  # Add the coin's weight (not just 1) to the total

    # --- Extra Task #2: Speed up the enemy every COIN_SPEED_THRESHOLD coin-points ---
    # Check if the player has crossed the next milestone
    while COINS >= next_speed_up:
        SPEED += 1                              # Increase enemy speed by 1
        next_speed_up += COIN_SPEED_THRESHOLD   # Set the next milestone

    # --- Check if player collided with an enemy ---
    if pygame.sprite.spritecollideany(P1, enemies):
        # Play crash sound if the file exists
        try:
            pygame.mixer.Sound('resources/crash.wav').play()
            time.sleep(0.5)
        except:
            pass  # Skip sound if file is missing

        # Show red screen with "Game Over" text
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_text, (30, 250))

        # Show final score and coins collected on the game over screen
        final_score = font_small.render("Score: " + str(SCORE), True, BLACK)
        final_coins = font_small.render("Coins: " + str(COINS), True, BLACK)
        DISPLAYSURF.blit(final_score, (150, 350))
        DISPLAYSURF.blit(final_coins, (150, 380))

        pygame.display.update()

        # Remove all sprites from the screen
        for entity in all_sprites:
            entity.kill()

        time.sleep(2)   # Wait 2 seconds before closing
        pygame.quit()
        sys.exit()

    # --- Update the display with everything drawn this frame ---
    pygame.display.update()

    # --- Limit the game to 60 FPS ---
    FramePerSec.tick(FPS)
