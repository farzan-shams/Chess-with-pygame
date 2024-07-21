import pygame
import os

from sound import Sound

class Config:
    def __init__(self):
        self.font = pygame.font.SysFont('monospace', 18, bold=True)
        self.move_sound = Sound(os.path.join('sounds/move-self.mp3'))
        self.capture_sound = Sound(os.path.join('sounds/capture.mp3'))

        