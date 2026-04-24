
import pygame
import sys
from player import MusicPlayer


def main():
    """Main function to run the Music Player."""
    pygame.init()
    pygame.mixer.init()

    
    WIDTH, HEIGHT = 600, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Music Player - Keyboard Controller")

    player = MusicPlayer(screen, WIDTH, HEIGHT)
    fps_clock = pygame.time.Clock()

    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                player.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.previous_track()
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    player.stop()
                    pygame.quit()
                    sys.exit()

        player.update()
        player.draw()
        pygame.display.flip()
        fps_clock.tick(30)


if __name__ == "__main__":
    main()
