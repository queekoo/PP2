import pygame


def main():
    pygame.init()

    # --- Screen setup ---
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Paint")
    clock = pygame.time.Clock()

    # --- Canvas: a separate surface where we draw permanently ---
    # This way the toolbar doesn't get erased when we redraw
    canvas = pygame.Surface((800, 550))
    canvas.fill((255, 255, 255))  # White canvas background

    # --- Font for toolbar labels ---
    font = pygame.font.SysFont(None, 22)

    # ─── Tool state ───────────────────────────────────────────
    # Current tool: 'pen', 'rectangle', 'circle', 'eraser'
    current_tool = 'pen'

    # Current drawing color
    current_color = (0, 0, 0)  # Default: black

    # Brush/eraser radius
    radius = 5

    # For pen: store trail of points to draw smooth lines
    points = []

    # For rectangle and circle: store the starting point on mouse press
    start_pos = None
    drawing_shape = False   # True while user is dragging to draw a shape

    # ─── Color palette ────────────────────────────────────────
    # Extra Task #4: list of colors the user can pick from
    palette_colors = [
        (0, 0, 0),        # Black
        (255, 255, 255),  # White
        (255, 0, 0),      # Red
        (0, 200, 0),      # Green
        (0, 0, 255),      # Blue
        (255, 165, 0),    # Orange
        (128, 0, 128),    # Purple
        (255, 255, 0),    # Yellow
        (0, 255, 255),    # Cyan
        (139, 69, 19),    # Brown
    ]

    # ─── Toolbar layout ───────────────────────────────────────
    # The toolbar sits at the bottom 50px of the window
    TOOLBAR_Y = 550      # Y position where toolbar starts
    TOOLBAR_H = 50       # Height of toolbar

    # Tool buttons: (label, tool_name, x position)
    tool_buttons = [
        ("Pen",   'pen',       10),
        ("Rect",  'rectangle', 80),
        ("Circle",'circle',   155),
        ("Eraser",'eraser',   235),
    ]
    BUTTON_W = 65
    BUTTON_H = 30

    # Color swatches start at x=320, each is 28x28 px
    SWATCH_SIZE = 28
    SWATCH_START_X = 320
    SWATCH_Y = TOOLBAR_Y + 11


    # ══════════════════════════════════════════════════════════
    #  Helper: draw the toolbar
    # ══════════════════════════════════════════════════════════
    def draw_toolbar():
        # Toolbar background
        pygame.draw.rect(screen, (220, 220, 220), (0, TOOLBAR_Y, 800, TOOLBAR_H))
        pygame.draw.line(screen, (150, 150, 150), (0, TOOLBAR_Y), (800, TOOLBAR_Y), 2)

        # Draw each tool button
        for label, tool, bx in tool_buttons:
            by = TOOLBAR_Y + 10
            # Highlight the currently selected tool
            color = (100, 180, 255) if tool == current_tool else (180, 180, 180)
            pygame.draw.rect(screen, color, (bx, by, BUTTON_W, BUTTON_H), border_radius=5)
            pygame.draw.rect(screen, (80, 80, 80), (bx, by, BUTTON_W, BUTTON_H), 1, border_radius=5)
            text = font.render(label, True, (0, 0, 0))
            screen.blit(text, (bx + BUTTON_W // 2 - text.get_width() // 2,
                                by + BUTTON_H // 2 - text.get_height() // 2))

        # Draw color swatches (Extra Task #4)
        for i, color in enumerate(palette_colors):
            sx = SWATCH_START_X + i * (SWATCH_SIZE + 4)
            pygame.draw.rect(screen, color, (sx, SWATCH_Y, SWATCH_SIZE, SWATCH_SIZE))
            # Highlight the currently selected color with a white border
            border_color = (255, 255, 255) if color == current_color else (80, 80, 80)
            pygame.draw.rect(screen, border_color, (sx, SWATCH_Y, SWATCH_SIZE, SWATCH_SIZE), 2)

        # Show current color preview and brush size
        preview_x = SWATCH_START_X + len(palette_colors) * (SWATCH_SIZE + 4) + 10
        pygame.draw.rect(screen, current_color, (preview_x, SWATCH_Y, SWATCH_SIZE, SWATCH_SIZE))
        pygame.draw.rect(screen, (0, 0, 0), (preview_x, SWATCH_Y, SWATCH_SIZE, SWATCH_SIZE), 2)

        size_text = font.render(f"Size: {radius}", True, (0, 0, 0))
        screen.blit(size_text, (preview_x + SWATCH_SIZE + 6, SWATCH_Y + 6))


    # ══════════════════════════════════════════════════════════
    #  Helper: draw a smooth line between two points (from tutorial)
    # ══════════════════════════════════════════════════════════
    def draw_line_between(surface, start, end, width, color):
        dx = start[0] - end[0]
        dy = start[1] - end[1]
        iterations = max(abs(dx), abs(dy))
        if iterations == 0:
            pygame.draw.circle(surface, color, start, width)
            return
        for i in range(iterations):
            progress = i / iterations
            aprogress = 1 - progress
            x = int(aprogress * start[0] + progress * end[0])
            y = int(aprogress * start[1] + progress * end[1])
            pygame.draw.circle(surface, color, (x, y), width)


    # ══════════════════════════════════════════════════════════
    #  Main loop
    # ══════════════════════════════════════════════════════════
    while True:

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # Is the mouse on the canvas (not toolbar)?
        on_canvas = mouse_pos[1] < TOOLBAR_Y

        for event in pygame.event.get():

            # --- Quit ---
            if event.type == pygame.QUIT:
                return

            # --- Keyboard shortcuts ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                # Change brush size with + and -
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    radius = min(50, radius + 1)
                if event.key == pygame.K_MINUS:
                    radius = max(1, radius - 1)
                # Tool shortcuts
                if event.key == pygame.K_p:
                    current_tool = 'pen'
                if event.key == pygame.K_r:
                    current_tool = 'rectangle'
                if event.key == pygame.K_c:
                    current_tool = 'circle'
                if event.key == pygame.K_e:
                    current_tool = 'eraser'

            # --- Mouse scroll: change brush size ---
            if event.type == pygame.MOUSEWHEEL:
                radius = max(1, min(50, radius + event.y))

            # --- Mouse button DOWN ---
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Left click on toolbar: check tool buttons and color swatches
                if event.button == 1 and not on_canvas:
                    # Check tool buttons
                    for label, tool, bx in tool_buttons:
                        by = TOOLBAR_Y + 10
                        btn_rect = pygame.Rect(bx, by, BUTTON_W, BUTTON_H)
                        if btn_rect.collidepoint(mouse_pos):
                            current_tool = tool

                    # Extra Task #4: Check color swatches
                    for i, color in enumerate(palette_colors):
                        sx = SWATCH_START_X + i * (SWATCH_SIZE + 4)
                        swatch_rect = pygame.Rect(sx, SWATCH_Y, SWATCH_SIZE, SWATCH_SIZE)
                        if swatch_rect.collidepoint(mouse_pos):
                            current_color = color

                # Left click on canvas: start drawing
                if event.button == 1 and on_canvas:
                    if current_tool in ('rectangle', 'circle'):
                        # Save start position for shape drawing
                        start_pos = mouse_pos
                        drawing_shape = True
                    elif current_tool == 'pen':
                        points = [mouse_pos]
                    elif current_tool == 'eraser':
                        points = [mouse_pos]

                # Right click: increase brush size
                if event.button == 3:
                    radius = min(50, radius + 2)

            # --- Mouse button UP: finish drawing rectangle or circle ---
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing_shape and start_pos:
                    end_pos = mouse_pos

                    # Extra Task #1: Draw rectangle on canvas
                    if current_tool == 'rectangle':
                        x = min(start_pos[0], end_pos[0])
                        y = min(start_pos[1], end_pos[1])
                        w = abs(end_pos[0] - start_pos[0])
                        h = abs(end_pos[1] - start_pos[1])
                        pygame.draw.rect(canvas, current_color, (x, y, w, h), radius)

                    # Extra Task #2: Draw circle on canvas
                    elif current_tool == 'circle':
                        cx = (start_pos[0] + end_pos[0]) // 2
                        cy = (start_pos[1] + end_pos[1]) // 2
                        r = int(((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2) ** 0.5 // 2)
                        if r > 0:
                            pygame.draw.circle(canvas, current_color, (cx, cy), r, radius)

                    drawing_shape = False
                    start_pos = None
                    points = []

            # --- Mouse motion: pen and eraser draw continuously ---
            if event.type == pygame.MOUSEMOTION and on_canvas:
                if mouse_pressed[0]:  # Left button held

                    if current_tool == 'pen':
                        # Add point and draw smooth line on canvas
                        points.append(mouse_pos)
                        if len(points) >= 2:
                            draw_line_between(canvas, points[-2], points[-1], radius, current_color)

                    elif current_tool == 'eraser':
                        # Extra Task #3: Eraser — draw white over the canvas
                        points.append(mouse_pos)
                        if len(points) >= 2:
                            draw_line_between(canvas, points[-2], points[-1], radius * 3, (255, 255, 255))

        # ─── Render ───────────────────────────────────────────

        # Draw the canvas onto the screen
        screen.blit(canvas, (0, 0))

        # Preview shape while dragging (before mouse release)
        if drawing_shape and start_pos and on_canvas:
            end_pos = mouse_pos
            # Extra Task #1: Rectangle preview
            if current_tool == 'rectangle':
                x = min(start_pos[0], end_pos[0])
                y = min(start_pos[1], end_pos[1])
                w = abs(end_pos[0] - start_pos[0])
                h = abs(end_pos[1] - start_pos[1])
                pygame.draw.rect(screen, current_color, (x, y, w, h), 2)

            # Extra Task #2: Circle preview
            elif current_tool == 'circle':
                cx = (start_pos[0] + end_pos[0]) // 2
                cy = (start_pos[1] + end_pos[1]) // 2
                r = int(((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2) ** 0.5 // 2)
                if r > 0:
                    pygame.draw.circle(screen, current_color, (cx, cy), r, 2)

        # Draw toolbar on top
        draw_toolbar()

        pygame.display.flip()
        clock.tick(60)


main()
