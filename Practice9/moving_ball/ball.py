"""
Ball Class
Represents the red ball with movement and boundary checking.
"""

import pygame


class Ball:
    """
    A red ball that moves on the screen by keyboard input.

    Specifications (from task):
    - Size: 50x50 pixels bounding box, radius = 25
    - Color: Red
    - Each arrow key press moves the ball by 20 pixels
    - Ball cannot leave the screen boundaries
    """

    STEP = 20          # Pixels per key press
    RADIUS = 25        # Ball radius (50x50 bounding box)
    COLOR = (220, 50, 50)        # Red
    BORDER_COLOR = (150, 20, 20) # Darker red border

    def __init__(self, x: int, y: int, radius: int,
                 screen_width: int, screen_height: int):
        """
        Initialize the ball.

        Args:
            x, y          : initial center position
            radius        : ball radius in pixels
            screen_width  : screen width  (used for boundary checks)
            screen_height : screen height (used for boundary checks)
        """
        self.radius = radius
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Start position clamped to valid area
        self.x = self._clamp_x(x)
        self.y = self._clamp_y(y)

    # ------------------------------------------------------------------
    # Boundary helpers
    # ------------------------------------------------------------------

    def _clamp_x(self, x: int) -> int:
        """Keep x within [radius, screen_width - radius]."""
        return max(self.radius, min(x, self.screen_width - self.radius))

    def _clamp_y(self, y: int) -> int:
        """Keep y within [radius, screen_height - radius]."""
        return max(self.radius, min(y, self.screen_height - self.radius))

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def move(self, dx: int, dy: int):
        """
        Attempt to move the ball by (dx, dy).
        Movement is ignored if it would push the ball off-screen.
        """
        new_x = self.x + dx
        new_y = self.y + dy

        # Only apply movement if it stays within bounds
        if self.radius <= new_x <= self.screen_width - self.radius:
            self.x = new_x
        # else: ignore the input (ball stays at current x)

        if self.radius <= new_y <= self.screen_height - self.radius:
            self.y = new_y
        # else: ignore the input (ball stays at current y)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface):
        """Draw the ball on the given surface."""
        # Filled circle
        pygame.draw.circle(screen, self.COLOR, (self.x, self.y), self.radius)
        # Border for visual depth
        pygame.draw.circle(screen, self.BORDER_COLOR, (self.x, self.y), self.radius, 3)
        # Small white highlight dot
        highlight_x = self.x - self.radius // 3
        highlight_y = self.y - self.radius // 3
        pygame.draw.circle(screen, (255, 255, 255), (highlight_x, highlight_y), 5)
