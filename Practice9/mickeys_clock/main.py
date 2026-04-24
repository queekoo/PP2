"""
Mickey's Clock Application - Main Entry Point
Practice 09: Game Development with Pygame
"""

import pygame
import sys
from clock import MickeysClock


def main():
    """Main function to run Mickey's Clock application."""
    pygame.init()

  
    WIDTH, HEIGHT = 500, 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey's Clock")

    clock_app = MickeysClock(screen, WIDTH, HEIGHT)
    fps_clock = pygame.time.Clock()

    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        clock_app.update()
        clock_app.draw()
        pygame.display.flip()
        fps_clock.tick(1)  


if __name__ == "__main__":
    main()
