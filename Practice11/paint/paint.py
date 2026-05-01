import pygame
import sys
import math


WIDTH,  HEIGHT     = 900, 650
TOOLBAR_HEIGHT     = 60
CANVAS_TOP         = TOOLBAR_HEIGHT
CANVAS_H           = HEIGHT - TOOLBAR_HEIGHT


BLACK     = (  0,   0,   0)
WHITE     = (255, 255, 255)
GRAY      = (200, 200, 200)
DARK_GRAY = ( 80,  80,  80)
LIGHT_BG  = (240, 240, 240)


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

SWATCH_SIZE   = 32
SWATCH_MARGIN = 4


TOOL_NAMES = ["Pencil", "Rectangle", "Square", "Circle",
              "RightTri", "EqTri", "Rhombus", "Eraser"]

TOOL_W      = 80   # Button width (slightly narrower to fit all tools)
ERASER_SIZE = 20   # Eraser brush radius


def draw_button(surface, font, label, rect, active, hover):
    """Draw a toolbar button with active/hover highlight."""
    color = (80, 130, 200) if active else ((150, 150, 150) if hover else DARK_GRAY)
    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=6)
    text = font.render(label, True, WHITE)
    surface.blit(text, text.get_rect(center=rect.center))




def draw_square(surface, color, start, end, width=2):
    """
    Draw a square. The side length is the shorter of the
    horizontal / vertical distances from start to end,
    keeping the top-left corner fixed at start.
    """
    x1, y1 = start
    x2, y2 = end
    # Side = minimum of width and height deltas, preserving sign for direction
    side = min(abs(x2 - x1), abs(y2 - y1))
    sx = side if x2 >= x1 else -side
    sy = side if y2 >= y1 else -side
    rect = pygame.Rect(min(x1, x1 + sx), min(y1, y1 + sy), side, side)
    pygame.draw.rect(surface, color, rect, width)


def draw_right_triangle(surface, color, start, end, width=2):
    """
    Draw a right-angle triangle.
    The right angle is at start.
    Vertices: start, (end_x, start_y), end  — forms an L shape.
    """
    x1, y1 = start
    x2, y2 = end
    # Right angle at top-left, horizontal leg along x, vertical leg along y
    points = [
        (x1, y1),          # right-angle corner
        (x2, y1),          # end of horizontal leg
        (x2, y2),          # far corner
    ]
    pygame.draw.polygon(surface, color, points, width)


def draw_equilateral_triangle(surface, color, start, end, width=2):
    
    x1, y1 = start
    x2, y2 = end
    base_len  = x2 - x1                      # Signed base length
    apex_h    = base_len * (3 ** 0.5) / 2    # Height of equilateral triangle
    # Apex direction: go toward end_y to follow the drag direction
    direction = 1 if y2 >= y1 else -1
    points = [
        (x1, y1),                             # base left
        (x2, y1),                             # base right
        (x1 + base_len / 2, y1 + direction * apex_h),  # apex
    ]
    pygame.draw.polygon(surface, color, points, width)


def draw_rhombus(surface, color, start, end, width=2):
  vertices are the midpoints of the bounding box sides.
   
    x1, y1 = start
    x2, y2 = end
    mx = (x1 + x2) / 2   # Horizontal midpoint
    my = (y1 + y2) / 2   # Vertical midpoint
    points = [
        (mx, y1),   # top
        (x2, my),   # right
        (mx, y2),   # bottom
        (x1, my),   # left
    ]
    pygame.draw.polygon(surface, color, points, width)



def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paint – Practice 11")
    clock = pygame.time.Clock()

    font       = pygame.font.SysFont("consolas", 14, bold=True)
    font_label = pygame.font.SysFont("consolas", 13)

    # Canvas is a Surface we draw on persistently
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill(WHITE)

    current_tool   = "Pencil"
    current_color  = BLACK
    draw_start     = None     # Canvas-space coordinates where the drag started
    drawing        = False
    preview_canvas = None     # Snapshot of canvas taken at drag-start (for shape preview)

    tool_rects = {}
    for i, name in enumerate(TOOL_NAMES):
        x = 10 + i * (TOOL_W + 4)
        tool_rects[name] = pygame.Rect(x, 10, TOOL_W, 40)

   
    palette_rects = []
    px_start = 10 + len(TOOL_NAMES) * (TOOL_W + 4) + 12
    for i, color in enumerate(PALETTE):
        x = px_start + i * (SWATCH_SIZE + SWATCH_MARGIN)
        rect = pygame.Rect(x, (TOOLBAR_HEIGHT - SWATCH_SIZE) // 2, SWATCH_SIZE, SWATCH_SIZE)
        palette_rects.append((rect, color))


    last_canvas_pos = None


    while True:
        mouse_pos    = pygame.mouse.get_pos()
       
        canvas_mouse = (mouse_pos[0], mouse_pos[1] - CANVAS_TOP)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_tool = False
                for name, rect in tool_rects.items():
                    if rect.collidepoint(mouse_pos):
                        current_tool = name
                        clicked_tool = True
                        break

                clicked_palette = False
                for rect, color in palette_rects:
                    if rect.collidepoint(mouse_pos):
                        current_color   = color
                        clicked_palette = True
                        
                        if current_tool == "Eraser":
                            current_tool = "Pencil"
                        break

               
                if not clicked_tool and not clicked_palette and mouse_pos[1] >= CANVAS_TOP:
                    drawing        = True
                    draw_start     = canvas_mouse
                    preview_canvas = canvas.copy()   # Snapshot for shape preview
                    last_canvas_pos = canvas_mouse   # FIX: initialise pencil start point

          
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and draw_start and mouse_pos[1] >= CANVAS_TOP:

                    if current_tool == "Rectangle":
                        x1, y1 = draw_start
                        x2, y2 = canvas_mouse
                        rect = pygame.Rect(min(x1, x2), min(y1, y2),
                                           abs(x2 - x1), abs(y2 - y1))
                        pygame.draw.rect(canvas, current_color, rect, 2)

                    elif current_tool == "Square":
                      
                        draw_square(canvas, current_color, draw_start, canvas_mouse)

                    elif current_tool == "Circle":
                        x1, y1 = draw_start
                        x2, y2 = canvas_mouse
                        radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
                        if radius > 0:
                            pygame.draw.circle(canvas, current_color, draw_start, radius, 2)

                    elif current_tool == "RightTri":
                        draw_right_triangle(canvas, current_color, draw_start, canvas_mouse)

                    elif current_tool == "EqTri":
                        
                        draw_equilateral_triangle(canvas, current_color, draw_start, canvas_mouse)

                    elif current_tool == "Rhombus":
                        
                        draw_rhombus(canvas, current_color, draw_start, canvas_mouse)

                drawing         = False
                draw_start      = None
                last_canvas_pos = None

            if event.type == pygame.MOUSEMOTION and drawing and mouse_pos[1] >= CANVAS_TOP:

                if current_tool == "Pencil":
               \
                    if last_canvas_pos is not None:
                        pygame.draw.line(canvas, current_color,
                                         last_canvas_pos, canvas_mouse, 3)
                    last_canvas_pos = canvas_mouse

                elif current_tool == "Eraser":
                    pygame.draw.circle(canvas, WHITE, canvas_mouse, ERASER_SIZE)

      
   
        screen.fill(DARK_GRAY)
        pygame.draw.rect(screen, (60, 60, 60), (0, 0, WIDTH, TOOLBAR_HEIGHT))

        for name, rect in tool_rects.items():
            hover = rect.collidepoint(mouse_pos)
            draw_button(screen, font, name, rect, name == current_tool, hover)

        for rect, color in palette_rects:
            pygame.draw.rect(screen, color, rect, border_radius=4)
            if color == current_color:
                pygame.draw.rect(screen, WHITE, rect, 3, border_radius=4)
            else:
                pygame.draw.rect(screen, DARK_GRAY, rect, 1, border_radius=4)

        lbl = font_label.render("Color:", True, GRAY)
        screen.blit(lbl, (px_start - 52, (TOOLBAR_HEIGHT - lbl.get_height()) // 2))

  
        if drawing and preview_canvas and draw_start:
            display_canvas = preview_canvas.copy()
            cx, cy = canvas_mouse
            sx, sy = draw_start

            if current_tool == "Rectangle":
                rect = pygame.Rect(min(sx, cx), min(sy, cy),
                                   abs(cx - sx), abs(cy - sy))
                pygame.draw.rect(display_canvas, current_color, rect, 2)

            elif current_tool == "Square":
                draw_square(display_canvas, current_color, draw_start, canvas_mouse)

            elif current_tool == "Circle":
                radius = int(((cx - sx) ** 2 + (cy - sy) ** 2) ** 0.5)
                if radius > 0:
                    pygame.draw.circle(display_canvas, current_color, draw_start, radius, 2)

            elif current_tool == "RightTri":
                draw_right_triangle(display_canvas, current_color, draw_start, canvas_mouse)

            elif current_tool == "EqTri":
                draw_equilateral_triangle(display_canvas, current_color, draw_start, canvas_mouse)

            elif current_tool == "Rhombus":
                draw_rhombus(display_canvas, current_color, draw_start, canvas_mouse)

            elif current_tool == "Eraser":
                pygame.draw.circle(display_canvas, WHITE, canvas_mouse, ERASER_SIZE)

            screen.blit(display_canvas, (0, CANVAS_TOP))
        else:
            screen.blit(canvas, (0, CANVAS_TOP))

        if current_tool == "Eraser" and mouse_pos[1] >= CANVAS_TOP:
            pygame.draw.circle(screen, DARK_GRAY, mouse_pos, ERASER_SIZE, 2)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
