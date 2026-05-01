import pygame
from persistence import load_leaderboard, load_settings, save_settings

# Colors
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (180, 180, 180)
DARK_GRAY  = ( 50,  50,  50)
RED        = (220,  50,  50)
GREEN      = ( 50, 200,  50)
BLUE       = ( 50, 120, 220)
YELLOW     = (255, 200,   0)
ORANGE     = (255, 140,   0)
DARK_BG    = ( 20,  20,  30)
PANEL      = ( 35,  35,  50)


def draw_button(surface, font, label, rect, hover=False, color=None):
    """Draw a rounded button. Returns True if hovered."""
    bg = color if color else (BLUE if hover else (60, 60, 90))
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, GRAY, rect, 2, border_radius=8)
    text = font.render(label, True, WHITE)
    surface.blit(text, text.get_rect(center=rect.center))


# ============================================================
#  Main Menu Screen
#  Returns: "play", "leaderboard", "settings", "quit"
# ============================================================
def main_menu(screen, clock, W, H):
    font_title = pygame.font.SysFont("Verdana", 52, bold=True)
    font_btn   = pygame.font.SysFont("Verdana", 26)
    font_sub   = pygame.font.SysFont("Verdana", 18)

    buttons = {
        "play":        pygame.Rect(W//2 - 120, 240, 240, 55),
        "leaderboard": pygame.Rect(W//2 - 120, 310, 240, 55),
        "settings":    pygame.Rect(W//2 - 120, 380, 240, 55),
        "quit":        pygame.Rect(W//2 - 120, 450, 240, 55),
    }
    labels = {
        "play": "▶  Play",
        "leaderboard": "🏆  Leaderboard",
        "settings": "⚙  Settings",
        "quit": "✕  Quit",
    }

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for action, rect in buttons.items():
                    if rect.collidepoint(mouse):
                        return action

        screen.fill(DARK_BG)

        # Decorative road stripes
        for i in range(0, H, 40):
            pygame.draw.line(screen, (30, 30, 45), (0, i), (W, i), 1)

        title = font_title.render("RACER", True, YELLOW)
        screen.blit(title, title.get_rect(center=(W//2, 140)))
        sub = font_sub.render("TSIS3 Edition", True, GRAY)
        screen.blit(sub, sub.get_rect(center=(W//2, 200)))

        for action, rect in buttons.items():
            hover = rect.collidepoint(mouse)
            col   = RED if action == "quit" else (GREEN if action == "play" else None)
            draw_button(screen, font_btn, labels[action], rect, hover, col)

        pygame.display.flip()
        clock.tick(60)


# ============================================================
#  Username Entry Screen
#  Returns: entered username string
# ============================================================
def username_screen(screen, clock, W, H):
    font_title = pygame.font.SysFont("Verdana", 36, bold=True)
    font_input = pygame.font.SysFont("Verdana", 28)
    font_hint  = pygame.font.SysFont("Verdana", 18)
    name = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        screen.fill(DARK_BG)
        title = font_title.render("Enter Your Name", True, YELLOW)
        screen.blit(title, title.get_rect(center=(W//2, H//2 - 80)))

        # Input box
        box = pygame.Rect(W//2 - 150, H//2 - 20, 300, 50)
        pygame.draw.rect(screen, PANEL, box, border_radius=8)
        pygame.draw.rect(screen, YELLOW, box, 2, border_radius=8)
        name_surf = font_input.render(name + "|", True, WHITE)
        screen.blit(name_surf, name_surf.get_rect(center=box.center))

        hint = font_hint.render("Press Enter to start", True, GRAY)
        screen.blit(hint, hint.get_rect(center=(W//2, H//2 + 60)))

        pygame.display.flip()
        clock.tick(60)


# ============================================================
#  Settings Screen
#  Returns: updated settings dict
# ============================================================
def settings_screen(screen, clock, W, H):
    font_title = pygame.font.SysFont("Verdana", 36, bold=True)
    font_opt   = pygame.font.SysFont("Verdana", 22)
    font_btn   = pygame.font.SysFont("Verdana", 20)

    settings = load_settings()

    CAR_COLORS  = ["RED", "BLUE", "GREEN", "YELLOW"]
    DIFFICULTIES = ["Easy", "Normal", "Hard"]

    back_rect = pygame.Rect(W//2 - 80, H - 80, 160, 45)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Sound toggle
                sound_rect = pygame.Rect(W//2 + 60, 180, 120, 38)
                if sound_rect.collidepoint(mouse):
                    settings["sound"] = not settings["sound"]
                    save_settings(settings)

                # Car color cycle
                color_rect = pygame.Rect(W//2 + 60, 240, 120, 38)
                if color_rect.collidepoint(mouse):
                    idx = CAR_COLORS.index(settings["car_color"])
                    settings["car_color"] = CAR_COLORS[(idx + 1) % len(CAR_COLORS)]
                    save_settings(settings)

                # Difficulty cycle
                diff_rect = pygame.Rect(W//2 + 60, 300, 120, 38)
                if diff_rect.collidepoint(mouse):
                    idx = DIFFICULTIES.index(settings["difficulty"])
                    settings["difficulty"] = DIFFICULTIES[(idx + 1) % len(DIFFICULTIES)]
                    save_settings(settings)

                # Back
                if back_rect.collidepoint(mouse):
                    return settings

        screen.fill(DARK_BG)
        title = font_title.render("Settings", True, YELLOW)
        screen.blit(title, title.get_rect(center=(W//2, 120)))

        rows = [
            ("Sound",      str(settings["sound"]),      180),
            ("Car Color",  settings["car_color"],        240),
            ("Difficulty", settings["difficulty"],       300),
        ]
        for label, value, y in rows:
            lbl = font_opt.render(label + ":", True, GRAY)
            screen.blit(lbl, (W//2 - 160, y + 8))
            btn_rect = pygame.Rect(W//2 + 60, y, 120, 38)
            hover    = btn_rect.collidepoint(mouse)
            draw_button(screen, font_btn, value, btn_rect, hover)

        # Back button
        draw_button(screen, font_btn, "◀  Back", back_rect,
                    back_rect.collidepoint(mouse), RED)

        pygame.display.flip()
        clock.tick(60)


# ============================================================
#  Leaderboard Screen
# ============================================================
def leaderboard_screen(screen, clock, W, H):
    font_title = pygame.font.SysFont("Verdana", 36, bold=True)
    font_row   = pygame.font.SysFont("Verdana", 20)
    font_btn   = pygame.font.SysFont("Verdana", 20)

    board     = load_leaderboard()
    back_rect = pygame.Rect(W//2 - 80, H - 80, 160, 45)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mouse):
                    return

        screen.fill(DARK_BG)
        title = font_title.render("🏆  Top 10", True, YELLOW)
        screen.blit(title, title.get_rect(center=(W//2, 80)))

        # Header
        hdr = font_row.render(f"{'#':<4} {'Name':<18} {'Score':>8}  {'Dist':>6}m", True, GRAY)
        screen.blit(hdr, (W//2 - 180, 140))
        pygame.draw.line(screen, GRAY, (W//2 - 180, 162), (W//2 + 180, 162), 1)

        for i, entry in enumerate(board):
            color = YELLOW if i == 0 else (GRAY if i == 1 else (ORANGE if i == 2 else WHITE))
            row = font_row.render(
                f"{i+1:<4} {entry['name']:<18} {entry['score']:>8}  {entry['distance']:>6}",
                True, color)
            screen.blit(row, (W//2 - 180, 175 + i * 32))

        if not board:
            empty = font_row.render("No scores yet — be the first!", True, GRAY)
            screen.blit(empty, empty.get_rect(center=(W//2, 280)))

        draw_button(screen, font_btn, "◀  Back", back_rect,
                    back_rect.collidepoint(mouse), RED)

        pygame.display.flip()
        clock.tick(60)


# ============================================================
#  Game Over Screen
#  Returns: "retry" or "menu"
# ============================================================
def game_over_screen(screen, clock, W, H, score, distance, coins, username):
    font_title = pygame.font.SysFont("Verdana", 48, bold=True)
    font_stat  = pygame.font.SysFont("Verdana", 24)
    font_btn   = pygame.font.SysFont("Verdana", 22)

    retry_rect = pygame.Rect(W//2 - 130, H//2 + 80, 110, 48)
    menu_rect  = pygame.Rect(W//2 + 20,  H//2 + 80, 110, 48)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_rect.collidepoint(mouse): return "retry"
                if menu_rect.collidepoint(mouse):  return "menu"

        screen.fill(DARK_BG)

        title = font_title.render("GAME OVER", True, RED)
        screen.blit(title, title.get_rect(center=(W//2, H//2 - 120)))

        name_surf = font_stat.render(f"Player: {username}", True, YELLOW)
        screen.blit(name_surf, name_surf.get_rect(center=(W//2, H//2 - 50)))

        for text, y in [
            (f"Score:     {score}",        H//2 - 10),
            (f"Distance:  {int(distance)} m", H//2 + 25),
            (f"Coins:     {coins}",         H//2 + 60),
        ]:
            surf = font_stat.render(text, True, WHITE)
            screen.blit(surf, surf.get_rect(center=(W//2, y)))

        draw_button(screen, font_btn, "↺ Retry",    retry_rect, retry_rect.collidepoint(mouse), GREEN)
        draw_button(screen, font_btn, "⌂ Menu",     menu_rect,  menu_rect.collidepoint(mouse),  BLUE)

        pygame.display.flip()
        clock.tick(60)
