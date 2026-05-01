import pygame
import sys
from game import run_game, load_settings, save_settings, WIDTH, HEIGHT, CELL
from db   import init_db, save_result, get_personal_best, get_leaderboard

# ============================================================
#  Colors
# ============================================================
BLACK     = (  0,   0,   0)
WHITE     = (255, 255, 255)
GRAY      = (180, 180, 180)
DARK_BG   = ( 18,  18,  28)
PANEL     = ( 35,  35,  55)
RED       = (210,  50,  50)
GREEN     = ( 50, 200,  80)
BLUE      = ( 50, 120, 220)
YELLOW    = (255, 210,   0)
ORANGE    = (255, 140,   0)
CYAN      = (  0, 200, 200)
PURPLE    = (160,  50, 220)


def draw_btn(surface, font, label, rect, hover=False, color=None):
    bg = color if color else (BLUE if hover else (50, 50, 80))
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, GRAY, rect, 2, border_radius=8)
    txt = font.render(label, True, WHITE)
    surface.blit(txt, txt.get_rect(center=rect.center))


# ============================================================
#  Main Menu
# ============================================================
def main_menu(screen, clock):
    font_title = pygame.font.SysFont("Verdana", 50, bold=True)
    font_btn   = pygame.font.SysFont("Verdana", 24)
    font_sub   = pygame.font.SysFont("Verdana", 16)

    btns = {
        "play":        pygame.Rect(WIDTH//2 - 110, 220, 220, 50),
        "leaderboard": pygame.Rect(WIDTH//2 - 110, 285, 220, 50),
        "settings":    pygame.Rect(WIDTH//2 - 110, 350, 220, 50),
        "quit":        pygame.Rect(WIDTH//2 - 110, 415, 220, 50),
    }
    labels = {
        "play": "▶  Play", "leaderboard": "🏆  Leaderboard",
        "settings": "⚙  Settings", "quit": "✕  Quit",
    }

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for action, rect in btns.items():
                    if rect.collidepoint(mouse):
                        return action

        screen.fill(DARK_BG)
        title = font_title.render("SNAKE", True, GREEN)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 130)))
        sub = font_sub.render("TSIS4 Edition", True, GRAY)
        screen.blit(sub, sub.get_rect(center=(WIDTH//2, 185)))

        for action, rect in btns.items():
            col = RED if action == "quit" else (GREEN if action == "play" else None)
            draw_btn(screen, font_btn, labels[action], rect, rect.collidepoint(mouse), col)

        pygame.display.flip()
        clock.tick(60)


# ============================================================
#  Username Entry
# ============================================================
def username_screen(screen, clock):
    font_title = pygame.font.SysFont("Verdana", 32, bold=True)
    font_input = pygame.font.SysFont("Verdana", 26)
    font_hint  = pygame.font.SysFont("Verdana", 16)
    name = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        screen.fill(DARK_BG)
        title = font_title.render("Enter Your Name", True, YELLOW)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))

        box = pygame.Rect(WIDTH//2 - 140, HEIGHT//2 - 25, 280, 50)
        pygame.draw.rect(screen, PANEL, box, border_radius=8)
        pygame.draw.rect(screen, YELLOW, box, 2, border_radius=8)
        inp = font_input.render(name + "|", True, WHITE)
        screen.blit(inp, inp.get_rect(center=box.center))

        hint = font_hint.render("Press Enter to continue", True, GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 55)))

        pygame.display.flip()
        clock.tick(60)


# ============================================================
#  Leaderboard Screen
# ============================================================
def leaderboard_screen(screen, clock):
    font_title = pygame.font.SysFont("Verdana", 32, bold=True)
    font_row   = pygame.font.SysFont("Verdana", 17)
    font_btn   = pygame.font.SysFont("Verdana", 20)
    back_rect  = pygame.Rect(WIDTH//2 - 70, HEIGHT - 70, 140, 42)

    try:
        board = get_leaderboard()
    except Exception:
        board = []

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mouse):
                    return

        screen.fill(DARK_BG)
        title = font_title.render("🏆  Top 10", True, YELLOW)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 60)))

        hdr = font_row.render(f"{'#':<3} {'Name':<16} {'Score':>6}  {'Lvl':>4}  {'Date'}", True, GRAY)
        screen.blit(hdr, (40, 110))
        pygame.draw.line(screen, GRAY, (40, 132), (WIDTH - 40, 132), 1)

        for i, (uname, score, level, date) in enumerate(board):
            col = YELLOW if i == 0 else (GRAY if i == 1 else (ORANGE if i == 2 else WHITE))
            row = font_row.render(
                f"{i+1:<3} {uname:<16} {score:>6}  {level:>4}  {date}", True, col)
            screen.blit(row, (40, 145 + i * 34))

        if not board:
            empty = font_row.render("No scores yet!", True, GRAY)
            screen.blit(empty, empty.get_rect(center=(WIDTH//2, 280)))

        draw_btn(screen, font_btn, "◀  Back", back_rect, back_rect.collidepoint(mouse), RED)
        pygame.display.flip()
        clock.tick(60)


# ============================================================
#  Settings Screen
# ============================================================
def settings_screen(screen, clock):
    font_title = pygame.font.SysFont("Verdana", 32, bold=True)
    font_opt   = pygame.font.SysFont("Verdana", 20)
    font_btn   = pygame.font.SysFont("Verdana", 18)

    settings = load_settings()

    COLOR_OPTIONS = [
        ("Green",  [  0, 200,   0]),
        ("Blue",   [ 50, 120, 220]),
        ("Red",    [220,  50,  50]),
        ("Yellow", [230, 200,   0]),
        ("Cyan",   [  0, 200, 200]),
        ("Purple", [160,  50, 220]),
    ]

    back_rect  = pygame.Rect(WIDTH//2 - 80, HEIGHT - 80, 160, 44)

    # Find current color index
    def color_idx():
        for i, (_, c) in enumerate(COLOR_OPTIONS):
            if c == settings["snake_color"]:
                return i
        return 0

    cidx = color_idx()

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Grid toggle
                grid_rect = pygame.Rect(WIDTH//2 + 40, 180, 110, 36)
                if grid_rect.collidepoint(mouse):
                    settings["grid"] = not settings["grid"]
                    save_settings(settings)

                # Sound toggle
                sound_rect = pygame.Rect(WIDTH//2 + 40, 235, 110, 36)
                if sound_rect.collidepoint(mouse):
                    settings["sound"] = not settings["sound"]
                    save_settings(settings)

                # Color prev/next
                prev_rect = pygame.Rect(WIDTH//2 - 120, 295, 40, 36)
                next_rect = pygame.Rect(WIDTH//2 + 80,  295, 40, 36)
                if prev_rect.collidepoint(mouse):
                    cidx = (cidx - 1) % len(COLOR_OPTIONS)
                    settings["snake_color"] = COLOR_OPTIONS[cidx][1]
                    save_settings(settings)
                if next_rect.collidepoint(mouse):
                    cidx = (cidx + 1) % len(COLOR_OPTIONS)
                    settings["snake_color"] = COLOR_OPTIONS[cidx][1]
                    save_settings(settings)

                # Back
                if back_rect.collidepoint(mouse):
                    return

        screen.fill(DARK_BG)
        title = font_title.render("Settings", True, YELLOW)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 110)))

        # Grid row
        screen.blit(font_opt.render("Grid overlay:", True, GRAY), (80, 188))
        grid_rect = pygame.Rect(WIDTH//2 + 40, 180, 110, 36)
        draw_btn(screen, font_btn, "ON" if settings["grid"] else "OFF",
                 grid_rect, grid_rect.collidepoint(mouse),
                 GREEN if settings["grid"] else RED)

        # Sound row
        screen.blit(font_opt.render("Sound:", True, GRAY), (80, 243))
        sound_rect = pygame.Rect(WIDTH//2 + 40, 235, 110, 36)
        draw_btn(screen, font_btn, "ON" if settings["sound"] else "OFF",
                 sound_rect, sound_rect.collidepoint(mouse),
                 GREEN if settings["sound"] else RED)

        # Snake color row
        screen.blit(font_opt.render("Snake color:", True, GRAY), (80, 303))
        prev_rect = pygame.Rect(WIDTH//2 - 120, 295, 40, 36)
        next_rect = pygame.Rect(WIDTH//2 + 80,  295, 40, 36)
        draw_btn(screen, font_btn, "◀", prev_rect, prev_rect.collidepoint(mouse))
        draw_btn(screen, font_btn, "▶", next_rect, next_rect.collidepoint(mouse))
        cname, cval = COLOR_OPTIONS[cidx]
        pygame.draw.rect(screen, tuple(cval),
                         pygame.Rect(WIDTH//2 - 70, 295, 140, 36), border_radius=6)
        clbl = font_btn.render(cname, True, WHITE)
        screen.blit(clbl, clbl.get_rect(center=(WIDTH//2, 313)))

        draw_btn(screen, font_btn, "💾 Save & Back", back_rect,
                 back_rect.collidepoint(mouse), BLUE)

        pygame.display.flip()
        clock.tick(60)


# ============================================================
#  Game Over Screen
# ============================================================
def game_over_screen(screen, clock, score, level, personal_best, username):
    font_title = pygame.font.SysFont("Verdana", 44, bold=True)
    font_stat  = pygame.font.SysFont("Verdana", 22)
    font_btn   = pygame.font.SysFont("Verdana", 20)

    retry_rect = pygame.Rect(WIDTH//2 - 125, HEIGHT//2 + 80, 110, 46)
    menu_rect  = pygame.Rect(WIDTH//2 + 15,  HEIGHT//2 + 80, 110, 46)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_rect.collidepoint(mouse): return "retry"
                if menu_rect.collidepoint(mouse):  return "menu"

        screen.fill(DARK_BG)
        title = font_title.render("GAME OVER", True, RED)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))

        name_surf = font_stat.render(f"Player: {username}", True, YELLOW)
        screen.blit(name_surf, name_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))

        for text, y in [
            (f"Score:         {score}",          HEIGHT//2 - 20),
            (f"Level reached: {level}",           HEIGHT//2 + 15),
            (f"Personal best: {personal_best}",   HEIGHT//2 + 50),
        ]:
            surf = font_stat.render(text, True, WHITE)
            screen.blit(surf, surf.get_rect(center=(WIDTH//2, y)))

        draw_btn(screen, font_btn, "↺ Retry",  retry_rect, retry_rect.collidepoint(mouse), GREEN)
        draw_btn(screen, font_btn, "⌂ Menu",   menu_rect,  menu_rect.collidepoint(mouse),  BLUE)

        pygame.display.flip()
        clock.tick(60)


# ============================================================
#  Entry point
# ============================================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake – TSIS4")
    clock  = pygame.time.Clock()

    # Init DB (create tables if needed)
    try:
        init_db()
    except Exception as e:
        print(f"DB init failed: {e} — leaderboard disabled")

    username = "Player"

    while True:
        action = main_menu(screen, clock)

        if action == "quit":
            pygame.quit(); sys.exit()

        elif action == "settings":
            settings_screen(screen, clock)

        elif action == "leaderboard":
            leaderboard_screen(screen, clock)

        elif action == "play":
            username = username_screen(screen, clock)

            # Fetch personal best
            try:
                best = get_personal_best(username)
            except Exception:
                best = 0

            while True:
                score, level = run_game(screen, clock, username, best)

                # Save to DB
                try:
                    save_result(username, score, level)
                    best = max(best, score)
                except Exception as e:
                    print(f"DB save failed: {e}")

                result = game_over_screen(screen, clock, score, level, best, username)
                if result == "retry":
                    continue
                else:
                    break


if __name__ == "__main__":
    main()
