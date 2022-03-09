import pygame
from pygame.math import Vector2

from src.utils.particles import Particles

# Not actually an entity, I did not know where to put it

class FireManager:
    def __init__(self, positions):
        self.rects = [pygame.Rect(pos[0], pos[1], 16, 16) for pos in positions]
        self.activeTimers = [0 for _ in self.rects]
        self.particles = Particles((3,5), (0,16, -2,2), colors=[
            (255,128,0), (255,255,0), (255,0,0), (255,255,255)
        ])

        self.reset = False

    def draw(self, win, scroll):
        self.particles.draw(win, scroll)

    def update(self, delta, player):
        self.particles.update(delta)
        
        for i, r in enumerate(self.rects):
            if player.waterParticles.collideRect(r):
                self.activeTimers[i] = 2
            elif self.activeTimers[i] <= 0 and player.rect.colliderect(r):
                self.reset = True
            
            if self.activeTimers[i] <= 0.3:
                self.particles.emit(r.bottomleft, 0.25, (-20,20, -50,-100))
            if self.activeTimers[i] > 0:
                self.activeTimers[i] -= delta