import pygame
from pygame.math import Vector2

from src.entities.entity import Entity

class Enemy(Entity):
    def __init__(self, *args):
        super().__init__(*args)

        self.applyGravity, self.applyCollision = True, True
        
        self.speed = 3 * 16
        self.dir = 1
        self.vel.x = self.speed
    
    def update(self, delta, tilemap=None, colRects=None):
        if self.collisionDir & 0b0100 > 0 or self.collisionDir & 0b0001 > 0:
            self.dir *= -1
            self.vel.x = self.speed * self.dir
        
        super().update(delta, tilemap, colRects)