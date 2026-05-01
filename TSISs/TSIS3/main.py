import pygame
import sys
from ui import main_menu, username_screen, settings_screen, leaderboard_screen, game_over_screen
from racer import run_game
from persistence import save_score

SCREEN_W = 400
SCREEN_H = 600


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Racer – TSIS3")
    clock  = pygame.time.Clock()

    username = "Player"

    while True:
        # ---- Main Menu ----
        action = main_menu(screen, clock, SCREEN_W, SCREEN_H)

        if action == "quit":
            pygame.quit()
            sys.exit()

        elif action == "settings":
            settings_screen(screen, clock, SCREEN_W, SCREEN_H)

        elif action == "leaderboard":
            leaderboard_screen(screen, clock, SCREEN_W, SCREEN_H)

        elif action == "play":
            # Ask for username
            username = username_screen(screen, clock, SCREEN_W, SCREEN_H)

            # Game loop with retry support
            while True:
                score, distance, coins = run_game(screen, clock, username)

                # Save to leaderboard
                save_score(username, score, distance)

                # Game Over screen
                result = game_over_screen(screen, clock, SCREEN_W, SCREEN_H,
                                          score, distance, coins, username)
                if result == "retry":
                    continue   # Play again with same username
                else:
                    break      # Back to main menu


if __name__ == "__main__":
    main()
