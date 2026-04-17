"""
Music Player Logic
Handles playlist management, audio playback, and UI rendering.
"""

import pygame
import os
import glob


class MusicPlayer:
    """
    Interactive music player with keyboard controls.
    Supports MP3 and WAV files from the music/ folder.
    """

    # Colors
    BG_COLOR      = (20, 20, 40)
    PRIMARY       = (100, 180, 255)
    SECONDARY     = (180, 180, 180)
    HIGHLIGHT     = (255, 220, 50)
    WHITE         = (255, 255, 255)
    GREEN         = (80, 200, 120)
    RED           = (220, 80, 80)
    DARK_GRAY     = (50, 50, 70)
    PROGRESS_BG   = (60, 60, 80)
    PROGRESS_FG   = (100, 180, 255)

    def __init__(self, screen: pygame.Surface, width: int, height: int):
        self.screen = screen
        self.width = width
        self.height = height

        self.playlist: list[str] = []
        self.current_index: int = 0
        self.is_playing: bool = False
        self.playback_pos: float = 0.0   # seconds
        self.track_length: float = 0.0   # seconds

        
        self.font_title  = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_body   = pygame.font.SysFont("Arial", 22)
        self.font_small  = pygame.font.SysFont("Arial", 16)
        self.font_key    = pygame.font.SysFont("Consolas", 18, bold=True)

       
        self._load_playlist()

        
        self._elapsed_ms: int = 0

   

    def _load_playlist(self):
        """Scan music/ folder for WAV and MP3 files."""
        music_dir = os.path.join(os.path.dirname(__file__), "music","sample_tracks")
        if not os.path.isdir(music_dir):
            os.makedirs(music_dir, exist_ok=True)

        patterns = ["*.wav", "*.mp3", "*.ogg"]
        found: list[str] = []
        for pat in patterns:
            found.extend(glob.glob(os.path.join(music_dir, pat)))

        self.playlist = sorted(found)
        if not self.playlist:
            print("Warning: No audio files found in music/ folder.")

    def _current_track_name(self) -> str:
        """Return the filename (without path) of the current track."""
        if not self.playlist:
            return "No tracks found"
        return os.path.basename(self.playlist[self.current_index])

   

    def play(self):
        """Play or resume the current track."""
        if not self.playlist:
            return
        track = self.playlist[self.current_index]
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self.is_playing = True
            self._elapsed_ms = 0
            
            try:
                sound = pygame.mixer.Sound(track)
                self.track_length = sound.get_length()
            except Exception:
                self.track_length = 0.0
        except pygame.error as e:
            print(f"Error playing {track}: {e}")

    def stop(self):
        """Stop playback."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self._elapsed_ms = 0
        self.playback_pos = 0.0

    def next_track(self):
        """Move to the next track and play it."""
        if not self.playlist:
            return
        was_playing = self.is_playing
        self.stop()
        self.current_index = (self.current_index + 1) % len(self.playlist)
        if was_playing:
            self.play()

    def previous_track(self):
        """Move to the previous track and play it."""
        if not self.playlist:
            return
        was_playing = self.is_playing
        self.stop()
        self.current_index = (self.current_index - 1) % len(self.playlist)
        if was_playing:
            self.play()

   

    def update(self):
        """Update playback state (called every frame)."""
        if self.is_playing:
           
            if not pygame.mixer.music.get_busy():
                self.next_track()
            else:
                
                self._elapsed_ms += 1000 // 30  # ~30 FPS
                self.playback_pos = self._elapsed_ms / 1000.0

    def draw(self):
        """Render the music player UI."""
        self.screen.fill(self.BG_COLOR)

        title = self.font_title.render("🎵  Music Player", True, self.PRIMARY)
        self.screen.blit(title, (20, 15))

        
        track_name = self._current_track_name()
        status_color = self.GREEN if self.is_playing else self.RED
        status_text = "▶  PLAYING" if self.is_playing else "■  STOPPED"

        status_surf = self.font_body.render(status_text, True, status_color)
        self.screen.blit(status_surf, (20, 70))

        track_label = self.font_body.render(f"Track {self.current_index + 1}/{len(self.playlist) or 1}:", True, self.SECONDARY)
        self.screen.blit(track_label, (20, 105))

        name_surf = self.font_body.render(track_name, True, self.WHITE)
        self.screen.blit(name_surf, (20, 132))

       
        bar_x, bar_y = 20, 180
        bar_w, bar_h = self.width - 40, 18
        pygame.draw.rect(self.screen, self.PROGRESS_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=9)

        if self.track_length > 0:
            progress = min(self.playback_pos / self.track_length, 1.0)
        else:
            progress = 0.0

        if progress > 0:
            fill_w = int(bar_w * progress)
            pygame.draw.rect(self.screen, self.PROGRESS_FG, (bar_x, bar_y, fill_w, bar_h), border_radius=9)

    
        pos_str = self._fmt_time(self.playback_pos)
        len_str = self._fmt_time(self.track_length) if self.track_length else "--:--"
        pos_surf = self.font_small.render(pos_str, True, self.SECONDARY)
        len_surf = self.font_small.render(len_str, True, self.SECONDARY)
        self.screen.blit(pos_surf, (bar_x, bar_y + 22))
        self.screen.blit(len_surf, (bar_x + bar_w - len_surf.get_width(), bar_y + 22))

        
        list_y = 230
        list_label = self.font_small.render("PLAYLIST", True, self.SECONDARY)
        self.screen.blit(list_label, (20, list_y))
        list_y += 22

        for i, track in enumerate(self.playlist):
            name = os.path.basename(track)
            color = self.HIGHLIGHT if i == self.current_index else self.SECONDARY
            prefix = "▶ " if i == self.current_index else "  "
            entry = self.font_small.render(f"{prefix}{i+1}. {name}", True, color)
            self.screen.blit(entry, (20, list_y + i * 20))

        if not self.playlist:
            no_tracks = self.font_small.render("No audio files in music/ folder", True, self.RED)
            self.screen.blit(no_tracks, (20, list_y))

        keys = [
            ("[P]", "Play"),
            ("[S]", "Stop"),
            ("[N]", "Next"),
            ("[B]", "Back"),
            ("[Q]", "Quit"),
        ]
        key_x = 20
        key_y = self.height - 45
        pygame.draw.rect(self.screen, self.DARK_GRAY, (10, key_y - 8, self.width - 20, 40), border_radius=6)
        for key, label in keys:
            k_surf = self.font_key.render(key, True, self.HIGHLIGHT)
            l_surf = self.font_small.render(label, True, self.SECONDARY)
            self.screen.blit(k_surf, (key_x, key_y))
            self.screen.blit(l_surf, (key_x, key_y + 20))
            key_x += 110

    @staticmethod
    def _fmt_time(seconds: float) -> str:
        """Format seconds as MM:SS."""
        s = int(seconds)
        return f"{s // 60:02d}:{s % 60:02d}"
