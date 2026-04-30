import pygame
import sys


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
TOOL_NAMES    = ["Pencil", "Rectangle", "Circle", "Eraser"]
TOOL_W        = 90
ERASER_SIZE   = 20   # radius of the eraser brush


def draw_button(surface, font, label, rect, active, hover):
    color = (80, 130, 200) if active else ((150, 150, 150) if hover else DARK_GRAY)
    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=6)
    text = font.render(label, True, WHITE)
    surface.blit(text, text.get_rect(center=rect.center))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paint – Practice 10")
    clock  = pygame.time.Clock()

    font       = pygame.font.SysFont("consolas", 16, bold=True)
    font_label = pygame.font.SysFont("consolas", 13)

    
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill(WHITE)

    
    current_tool   = "Pencil"    
    current_color  = BLACK      
    draw_start     = None        
    drawing        = False      
    preview_canvas = None        

    
    tool_rects = {}
    for i, name in enumerate(TOOL_NAMES):
        x = 10 + i * (TOOL_W + 6)
        tool_rects[name] = pygame.Rect(x, 10, TOOL_W, 40)


    palette_rects = []
    px_start = 10 + len(TOOL_NAMES) * (TOOL_W + 6) + 20
    for i, color in enumerate(PALETTE):
        x = px_start + i * (SWATCH_SIZE + SWATCH_MARGIN)
        rect = pygame.Rect(x, (TOOLBAR_HEIGHT - SWATCH_SIZE) // 2, SWATCH_SIZE, SWATCH_SIZE)
        palette_rects.append((rect, color))


    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        canvas_mouse = (mouse_pos[0], mouse_pos[1] - CANVAS_TOP)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            
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
                        current_color  = color
                        clicked_palette = True
                        if current_tool == "Eraser":
                            current_tool = "Pencil"   
                        break

                
                if not clicked_tool and not clicked_palette and mouse_pos[1] >= CANVAS_TOP:
                    drawing        = True
                    draw_start     = canvas_mouse
                    preview_canvas = canvas.copy()  

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                
                if drawing and draw_start and mouse_pos[1] >= CANVAS_TOP:
                    if current_tool == "Rectangle":
                        
                        x1, y1 = draw_start
                        x2, y2 = canvas_mouse
                        rect = pygame.Rect(min(x1,x2), min(y1,y2),
                                           abs(x2-x1), abs(y2-y1))
                        pygame.draw.rect(canvas, current_color, rect, 2)

                    elif current_tool == "Circle":
                        
                        x1, y1 = draw_start
                        x2, y2 = canvas_mouse
                        radius = int(((x2-x1)**2 + (y2-y1)**2)**0.5)
                        if radius > 0:
                            pygame.draw.circle(canvas, current_color,
                                               draw_start, radius, 2)

                drawing    = False
                draw_start = None

            
            if event.type == pygame.MOUSEMOTION and drawing and mouse_pos[1] >= CANVAS_TOP:
                if current_tool == "Pencil":
                    # Draw continuous line segment between frames
                    prev = (mouse_pos[0] - event.rel[0],
                            mouse_pos[1] - event.rel[1] - CANVAS_TOP)
                    pygame.draw.line(canvas, current_color, prev, canvas_mouse, 3)

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
        screen.blit(lbl, (px_start - 50, (TOOLBAR_HEIGHT - lbl.get_height()) // 2))

        
        if drawing and preview_canvas and draw_start:

            display_canvas = preview_canvas.copy()
            cx, cy = canvas_mouse
            sx, sy = draw_start

            if current_tool == "Rectangle":
                rect = pygame.Rect(min(sx,cx), min(sy,cy),
                                   abs(cx-sx), abs(cy-sy))
                pygame.draw.rect(display_canvas, current_color, rect, 2)

            elif current_tool == "Circle":
                radius = int(((cx-sx)**2 + (cy-sy)**2)**0.5)
                if radius > 0:
                    pygame.draw.circle(display_canvas, current_color,
                                       draw_start, radius, 2)

            elif current_tool == "Eraser":
                pygame.draw.circle(display_canvas, WHITE, canvas_mouse, ERASER_SIZE)

            screen.blit(display_canvas, (0, CANVAS_TOP))
        else:
            screen.blit(canvas, (0, CANVAS_TOP))

        # Eraser cursor ring
        if current_tool == "Eraser" and mouse_pos[1] >= CANVAS_TOP:
            pygame.draw.circle(screen, DARK_GRAY, mouse_pos, ERASER_SIZE, 2)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()