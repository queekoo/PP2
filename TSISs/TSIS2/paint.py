import pygame
import sys
import math
import datetime
from collections import deque


WIDTH,  HEIGHT     = 960, 680
TOOLBAR_HEIGHT     = 100   # Two rows of toolbar
CANVAS_TOP         = TOOLBAR_HEIGHT
CANVAS_H           = HEIGHT - TOOLBAR_HEIGHT


BLACK     = (  0,   0,   0)
WHITE     = (255, 255, 255)
GRAY      = (200, 200, 200)
DARK_GRAY = ( 60,  60,  60)
MID_GRAY  = (100, 100, 100)
BLUE_HL   = ( 80, 130, 200)  # Active button highlight


PALETTE = [
    (  0,   0,   0),
    (255, 255, 255),
    (220,  50,  50),
    ( 50, 180,  50),
    ( 50, 100, 220),
    (255, 200,   0),
    (255, 130,   0),
    (150,  50, 200),
    (  0, 200, 200),
    (255, 150, 180),
    (120,  80,  40),
    (150, 150, 150),
]

SWATCH_SIZE   = 28
SWATCH_MARGIN = 3

# --- All tools including Practice 11 shapes + TSIS2 new tools ---
TOOL_NAMES = [
    "Pencil", "Line", "Rectangle", "Square", "Circle",
    "RightTri", "EqTri", "Rhombus", "Fill", "Text", "Eraser"
]

TOOL_W = 72   # Button width
TOOL_H = 34   # Button height

ERASER_SIZE = 20

# --- Brush sizes (px) for TSIS2 task 3.2 ---
BRUSH_SIZES  = [2, 5, 10]
BRUSH_LABELS = ["1:S", "2:M", "3:L"]


# ============================================================
#  Helper: draw a toolbar button
# ============================================================
def draw_button(surface, font, label, rect, active, hover):
    color = BLUE_HL if active else (MID_GRAY if hover else DARK_GRAY)
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, (180, 180, 180), rect, 1, border_radius=5)
    text = font.render(label, True, WHITE)
    surface.blit(text, text.get_rect(center=rect.center))


# ============================================================
#  Practice 11 shape helpers  (unchanged from Practice 11)
# ============================================================
def draw_square(surface, color, start, end, width=2):
    x1, y1 = start
    x2, y2 = end
    side = min(abs(x2 - x1), abs(y2 - y1))
    sx = side if x2 >= x1 else -side
    sy = side if y2 >= y1 else -side
    rect = pygame.Rect(min(x1, x1 + sx), min(y1, y1 + sy), side, side)
    pygame.draw.rect(surface, color, rect, width)

def draw_right_triangle(surface, color, start, end, width=2):
    x1, y1 = start
    x2, y2 = end
    points = [(x1, y1), (x2, y1), (x2, y2)]
    pygame.draw.polygon(surface, color, points, width)

def draw_equilateral_triangle(surface, color, start, end, width=2):
    x1, y1 = start
    x2, y2 = end
    base_len = x2 - x1
    apex_h   = base_len * (3 ** 0.5) / 2
    direction = 1 if y2 >= y1 else -1
    points = [
        (x1, y1),
        (x2, y1),
        (x1 + base_len / 2, y1 + direction * apex_h),
    ]
    pygame.draw.polygon(surface, color, points, width)

def draw_rhombus(surface, color, start, end, width=2):
    x1, y1 = start
    x2, y2 = end
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    points = [(mx, y1), (x2, my), (mx, y2), (x1, my)]
    pygame.draw.polygon(surface, color, points, width)


# ============================================================
#  TSIS2 Task 3.3 — Flood Fill (BFS)
#  Fills the area around (x, y) that shares the same color,
#  replacing it with fill_color.
# ============================================================
def flood_fill(surface, x, y, fill_color):
    target_color = surface.get_at((x, y))[:3]   # Ignore alpha
    fill_color   = fill_color[:3]

    # If the area is already the fill color, do nothing
    if target_color == fill_color:
        return

    w, h   = surface.get_size()
    visited = set()
    queue  = deque()
    queue.append((x, y))

    while queue:
        cx, cy = queue.popleft()

        # Skip out-of-bounds or already visited pixels
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            continue
        if (cx, cy) in visited:
            continue

        # Stop if this pixel is not the target color
        if surface.get_at((cx, cy))[:3] != target_color:
            continue

        surface.set_at((cx, cy), fill_color)
        visited.add((cx, cy))

        # Add 4-connected neighbours
        queue.append((cx + 1, cy))
        queue.append((cx - 1, cy))
        queue.append((cx, cy + 1))
        queue.append((cx, cy - 1))


# ============================================================
#  Main application
# ============================================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paint – TSIS2")
    clock = pygame.time.Clock()

    font       = pygame.font.SysFont("consolas", 13, bold=True)
    font_label = pygame.font.SysFont("consolas", 12)
    font_text  = pygame.font.SysFont("consolas", 22)   # Font used for text tool

    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill(WHITE)

    # --- State variables ---
    current_tool    = "Pencil"
    current_color   = BLACK
    brush_size_idx  = 0           # Index into BRUSH_SIZES (0=small, 1=medium, 2=large)
    draw_start      = None
    drawing         = False
    preview_canvas  = None
    last_canvas_pos = None

    # Text tool state
    text_active   = False    # True when user has clicked to place text cursor
    text_pos      = (0, 0)   # Canvas position where text will be placed
    text_buffer   = ""       # Characters typed so far

    # ============================================================
    #  Build toolbar layout — two rows
    #  Row 1: tool buttons (split into two rows if needed)
    #  Row 2: brush sizes + palette
    # ============================================================

    # Row 1: tools (all fit in one row with smaller buttons)
    tool_rects = {}
    for i, name in enumerate(TOOL_NAMES):
        x = 5 + i * (TOOL_W + 3)
        tool_rects[name] = pygame.Rect(x, 5, TOOL_W, TOOL_H)

    # Row 2: brush size buttons
    brush_rects = []
    for i, label in enumerate(BRUSH_LABELS):
        x = 5 + i * 52
        brush_rects.append(pygame.Rect(x, 46, 48, 26))

    # Row 2: palette swatches (after brush buttons)
    palette_rects = []
    px_start = 5 + len(BRUSH_LABELS) * 52 + 15
    for i, color in enumerate(PALETTE):
        x = px_start + i * (SWATCH_SIZE + SWATCH_MARGIN)
        rect = pygame.Rect(x, 48, SWATCH_SIZE, SWATCH_SIZE)
        palette_rects.append((rect, color))

    # ============================================================
    #  Main loop
    # ============================================================
    while True:
        mouse_pos    = pygame.mouse.get_pos()
        canvas_mouse = (mouse_pos[0], mouse_pos[1] - CANVAS_TOP)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ---- Keyboard events ----
            if event.type == pygame.KEYDOWN:

                # Brush size shortcuts: 1, 2, 3
                if event.key == pygame.K_1:
                    brush_size_idx = 0
                elif event.key == pygame.K_2:
                    brush_size_idx = 1
                elif event.key == pygame.K_3:
                    brush_size_idx = 2

                # TSIS2 Task 3.4 — Ctrl+S saves canvas as timestamped PNG
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename  = f"canvas_{timestamp}.png"
                    pygame.image.save(canvas, filename)
                    print(f"Saved: {filename}")

                # TSIS2 Task 3.5 — Text tool keyboard input
                elif text_active:
                    if event.key == pygame.K_RETURN:
                        # Confirm: render text permanently onto the canvas
                        if text_buffer:
                            text_surf = font_text.render(text_buffer, True, current_color)
                            canvas.blit(text_surf, text_pos)
                        text_active  = False
                        text_buffer  = ""

                    elif event.key == pygame.K_ESCAPE:
                        # Cancel text entry
                        text_active = False
                        text_buffer = ""

                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]

                    else:
                        # Append typed character (printable only)
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode

            # ---- Mouse button down ----
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # If text is active and user clicks elsewhere, cancel
                if text_active:
                    text_active = False
                    text_buffer = ""

                # Check tool buttons
                clicked_tool = False
                for name, rect in tool_rects.items():
                    if rect.collidepoint(mouse_pos):
                        current_tool = name
                        clicked_tool = True
                        break

                # Check brush size buttons
                clicked_brush = False
                for i, rect in enumerate(brush_rects):
                    if rect.collidepoint(mouse_pos):
                        brush_size_idx = i
                        clicked_brush  = True
                        break

                # Check palette swatches
                clicked_palette = False
                for rect, color in palette_rects:
                    if rect.collidepoint(mouse_pos):
                        current_color   = color
                        clicked_palette = True
                        if current_tool == "Eraser":
                            current_tool = "Pencil"
                        break

                # Canvas click
                if not clicked_tool and not clicked_brush and not clicked_palette \
                        and mouse_pos[1] >= CANVAS_TOP:

                    # Text tool: place cursor on canvas
                    if current_tool == "Text":
                        text_active = True
                        text_pos    = canvas_mouse
                        text_buffer = ""

                    # Fill tool: flood fill at click position
                    elif current_tool == "Fill":
                        flood_fill(canvas, canvas_mouse[0], canvas_mouse[1], current_color)

                    else:
                        drawing         = True
                        draw_start      = canvas_mouse
                        preview_canvas  = canvas.copy()
                        last_canvas_pos = canvas_mouse

            # ---- Mouse button up: commit shape ----
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                bsize = BRUSH_SIZES[brush_size_idx]

                if drawing and draw_start and mouse_pos[1] >= CANVAS_TOP:

                    if current_tool == "Line":
                        # TSIS2 Task 3.1 — straight line
                        pygame.draw.line(canvas, current_color, draw_start, canvas_mouse, bsize)

                    elif current_tool == "Rectangle":
                        x1, y1 = draw_start; x2, y2 = canvas_mouse
                        rect = pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
                        pygame.draw.rect(canvas, current_color, rect, bsize)

                    elif current_tool == "Square":
                        draw_square(canvas, current_color, draw_start, canvas_mouse, bsize)

                    elif current_tool == "Circle":
                        x1, y1 = draw_start; x2, y2 = canvas_mouse
                        radius = int(((x2-x1)**2 + (y2-y1)**2)**0.5)
                        if radius > 0:
                            pygame.draw.circle(canvas, current_color, draw_start, radius, bsize)

                    elif current_tool == "RightTri":
                        draw_right_triangle(canvas, current_color, draw_start, canvas_mouse, bsize)

                    elif current_tool == "EqTri":
                        draw_equilateral_triangle(canvas, current_color, draw_start, canvas_mouse, bsize)

                    elif current_tool == "Rhombus":
                        draw_rhombus(canvas, current_color, draw_start, canvas_mouse, bsize)

                drawing         = False
                draw_start      = None
                last_canvas_pos = None

            # ---- Mouse motion ----
            if event.type == pygame.MOUSEMOTION and drawing and mouse_pos[1] >= CANVAS_TOP:
                bsize = BRUSH_SIZES[brush_size_idx]

                if current_tool == "Pencil":
                    # TSIS2 Task 3.1 — continuous freehand drawing
                    if last_canvas_pos is not None:
                        pygame.draw.line(canvas, current_color,
                                         last_canvas_pos, canvas_mouse, bsize)
                    last_canvas_pos = canvas_mouse

                elif current_tool == "Eraser":
                    pygame.draw.circle(canvas, WHITE, canvas_mouse, ERASER_SIZE)

        # ============================================================
        #  Render
        # ============================================================
        screen.fill((45, 45, 45))
        pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, TOOLBAR_HEIGHT))
        pygame.draw.line(screen, (80, 80, 80), (0, TOOLBAR_HEIGHT - 1), (WIDTH, TOOLBAR_HEIGHT - 1))

        # Tool buttons (row 1)
        for name, rect in tool_rects.items():
            hover = rect.collidepoint(mouse_pos)
            draw_button(screen, font, name, rect, name == current_tool, hover)

        # Brush size buttons (row 2)
        for i, (rect, label) in enumerate(zip(brush_rects, BRUSH_LABELS)):
            hover  = rect.collidepoint(mouse_pos)
            active = (i == brush_size_idx)
            draw_button(screen, font, label, rect, active, hover)

        # Palette swatches (row 2)
        for rect, color in palette_rects:
            pygame.draw.rect(screen, color, rect, border_radius=3)
            if color == current_color:
                pygame.draw.rect(screen, WHITE, rect, 2, border_radius=3)
            else:
                pygame.draw.rect(screen, (80, 80, 80), rect, 1, border_radius=3)

        # "Color:" label
        lbl = font_label.render("Color:", True, GRAY)
        screen.blit(lbl, (px_start - 48, 54))

        # Current color preview square
        pygame.draw.rect(screen, current_color,
                         pygame.Rect(px_start - 48, 66, 42, 10), border_radius=2)

        # ---- Canvas: shape preview while dragging ----
        bsize = BRUSH_SIZES[brush_size_idx]

        if drawing and preview_canvas and draw_start:
            display_canvas = preview_canvas.copy()
            cx, cy = canvas_mouse
            sx, sy = draw_start

            if current_tool == "Line":
                pygame.draw.line(display_canvas, current_color, draw_start, canvas_mouse, bsize)

            elif current_tool == "Rectangle":
                rect = pygame.Rect(min(sx,cx), min(sy,cy), abs(cx-sx), abs(cy-sy))
                pygame.draw.rect(display_canvas, current_color, rect, bsize)

            elif current_tool == "Square":
                draw_square(display_canvas, current_color, draw_start, canvas_mouse, bsize)

            elif current_tool == "Circle":
                radius = int(((cx-sx)**2 + (cy-sy)**2)**0.5)
                if radius > 0:
                    pygame.draw.circle(display_canvas, current_color, draw_start, radius, bsize)

            elif current_tool == "RightTri":
                draw_right_triangle(display_canvas, current_color, draw_start, canvas_mouse, bsize)

            elif current_tool == "EqTri":
                draw_equilateral_triangle(display_canvas, current_color, draw_start, canvas_mouse, bsize)

            elif current_tool == "Rhombus":
                draw_rhombus(display_canvas, current_color, draw_start, canvas_mouse, bsize)

            elif current_tool == "Eraser":
                pygame.draw.circle(display_canvas, WHITE, canvas_mouse, ERASER_SIZE)

            screen.blit(display_canvas, (0, CANVAS_TOP))

        else:
            # Normal canvas display
            display_canvas = canvas.copy()

            # TSIS2 Task 3.5 — show live text preview while typing
            if text_active and text_buffer:
                preview_surf = font_text.render(text_buffer + "|", True, current_color)
                display_canvas.blit(preview_surf, text_pos)
            elif text_active:
                # Show blinking cursor even before typing
                cursor_surf = font_text.render("|", True, current_color)
                display_canvas.blit(cursor_surf, text_pos)

            screen.blit(display_canvas, (0, CANVAS_TOP))

        # Eraser cursor ring
        if current_tool == "Eraser" and mouse_pos[1] >= CANVAS_TOP:
            pygame.draw.circle(screen, GRAY, mouse_pos, ERASER_SIZE, 2)

        # Fill cursor crosshair
        if current_tool == "Fill" and mouse_pos[1] >= CANVAS_TOP:
            mx, my = mouse_pos
            pygame.draw.line(screen, BLACK, (mx - 8, my), (mx + 8, my), 2)
            pygame.draw.line(screen, BLACK, (mx, my - 8), (mx, my + 8), 2)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
