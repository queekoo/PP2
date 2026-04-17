"""
Mickey's Clock - Clock Logic
Displays current time using Mickey Mouse hand images as clock hands.
Right hand = minutes, Left hand = seconds.
"""

import pygame
import os
import math
import datetime


class MickeysClock:
    """
    A clock that uses Mickey Mouse hand images as clock hands.
    Right hand = minutes hand
    Left hand  = seconds hand
    """

    def __init__(self, screen: pygame.Surface, width: int, height: int):
        self.screen = screen
        self.width = width
        self.height = height
        self.center = (width // 2, height // 2)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY  = (200, 200, 200)

        # Load fonts
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 24)

        # Load Mickey hand image (used for both hands)
        self.hand_image = self._load_hand_image()

        # Clock face radius
        self.radius = min(width, height) // 2 - 30

    def _load_hand_image(self) -> pygame.Surface | None:
        """Load the Mickey Mouse hand image from images/ folder."""
        image_path = os.path.join(
            os.path.dirname(__file__), "images", "mickey_hand.png"
        )
        if os.path.exists(image_path):
            try:
                img = pygame.image.load(image_path).convert_alpha()
                # Scale hand to reasonable size
                img = pygame.transform.scale(img, (40, 120))
                return img
            except pygame.error:
                print(f"Warning: Could not load image at {image_path}")
        else:
            print(f"Warning: Image not found at {image_path}. Using drawn hands.")
        return None

    def _get_current_time(self) -> tuple[int, int]:
        """Return current (minutes, seconds)."""
        now = datetime.datetime.now()
        return now.minute, now.second

    def _angle_for(self, value: int, max_value: int) -> float:
        """
        Convert a time value to a rotation angle (degrees).
        12 o'clock position = -90 degrees (pointing up).
        Rotation is clockwise.
        """
        return (value / max_value) * 360 - 90

    def _draw_clock_face(self):
        """Draw the circular clock face with tick marks."""
        # Background
        self.screen.fill(self.WHITE)

        # Clock circle
        pygame.draw.circle(self.screen, self.BLACK, self.center, self.radius, 4)

        # Draw 60 tick marks
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            if i % 5 == 0:
                # Major tick (every 5 seconds / minutes)
                inner = self.radius - 20
                width = 3
            else:
                # Minor tick
                inner = self.radius - 10
                width = 1

            outer = self.radius - 4
            x1 = int(self.center[0] + inner * math.cos(angle))
            y1 = int(self.center[1] + inner * math.sin(angle))
            x2 = int(self.center[0] + outer * math.cos(angle))
            y2 = int(self.center[1] + outer * math.sin(angle))
            pygame.draw.line(self.screen, self.BLACK, (x1, y1), (x2, y2), width)

        # Center dot
        pygame.draw.circle(self.screen, self.BLACK, self.center, 8)

    def _draw_hand_image(self, angle_deg: float, length: int, color: tuple):
        """
        Draw a clock hand either as the Mickey image or as a line fallback.
        angle_deg: angle in degrees (0 = 3 o'clock, -90 = 12 o'clock)
        """
        angle_rad = math.radians(angle_deg)

        if self.hand_image:
            # Rotate image: pygame rotates counter-clockwise
            # Our angle is clockwise from top, convert accordingly
            rotated = pygame.transform.rotate(self.hand_image, -(angle_deg + 90))
            rect = rotated.get_rect(center=self.center)
            self.screen.blit(rotated, rect)
        else:
            # Fallback: draw a colored line
            end_x = int(self.center[0] + length * math.cos(angle_rad))
            end_y = int(self.center[1] + length * math.sin(angle_rad))
            pygame.draw.line(self.screen, color, self.center, (end_x, end_y), 6)
            # Hand tip circle
            pygame.draw.circle(self.screen, color, (end_x, end_y), 8)

    def _draw_time_text(self, minutes: int, seconds: int):
        """Display current time as text at the bottom."""
        time_str = f"{minutes:02d}:{seconds:02d}"
        label = self.font_large.render(time_str, True, self.BLACK)
        rect = label.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(label, rect)

        hint = self.font_small.render("Right=Minutes  Left=Seconds", True, self.GRAY)
        hint_rect = hint.get_rect(center=(self.width // 2, self.height - 15))
        self.screen.blit(hint, hint_rect)

    def update(self):
        """Update time (called once per second from main loop)."""
        # Nothing to store; we read time fresh in draw()
        pass

    def draw(self):
        """Draw the full clock."""
        minutes, seconds = self._get_current_time()

        self._draw_clock_face()

        # Minutes hand (right hand) — blue
        min_angle = self._angle_for(minutes, 60)
        self._draw_hand_image(min_angle, int(self.radius * 0.65), (0, 0, 200))

        # Seconds hand (left hand) — red, longer
        sec_angle = self._angle_for(seconds, 60)
        self._draw_hand_image(sec_angle, int(self.radius * 0.85), (200, 0, 0))

        # Re-draw center dot on top
        pygame.draw.circle(self.screen, self.BLACK, self.center, 8)

        # Time text
        self._draw_time_text(minutes, seconds)
