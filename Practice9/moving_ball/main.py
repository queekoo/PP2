"""
Moving Ball Game - Main Entry Point
Practice 09: Game Development with Pygame

Controls:
  Arrow Keys = Move the red ball (20 pixels per press)
  ESC        = Quit
"""

import pygame
import sys
from ball import Ball


def main():
    """Main function to run the Moving Ball Game."""
    pygame.init()

    # Window settings
    WIDTH, HEIGHT = 600, 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball Game")

    # Create the ball (starts in the center)
    ball = Ball(WIDTH // 2, HEIGHT // 2, radius=25, screen_width=WIDTH, screen_height=HEIGHT)

    fps_clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_UP:
                    ball.move(0, -Ball.STEP)
                elif event.key == pygame.K_DOWN:
                    ball.move(0, Ball.STEP)
                elif event.key == pygame.K_LEFT:
                    ball.move(-Ball.STEP, 0)
                elif event.key == pygame.K_RIGHT:
                    ball.move(Ball.STEP, 0)

        # Draw background
        screen.fill((255, 255, 255))

        # Draw ball
        ball.draw(screen)

        # HUD: position info
        info = font.render(
            f"Position: ({ball.x}, {ball.y})   Arrow keys to move   ESC to quit",
            True, (100, 100, 100)
        )
        screen.blit(info, (10, 10))

        pygame.display.flip()
        fps_clock.tick(60)


if __name__ == "__main__":
    main()
