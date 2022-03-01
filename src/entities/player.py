import pygame
from pygame.math import Vector2

from src.entities.entity import Entity

class Player(Entity):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        self.speed = 16*5
        self.jumpHeight = 150

        self.applyGravity, self.applyCollision = True, True
        
    def update(self, delta, tilemap=None, colRects=None):
        keys = pygame.key.get_pressed()

        self.vel.x *= 0.9

        if keys[pygame.K_d]:    self.vel.x =  self.speed
        if keys[pygame.K_a]:    self.vel.x = -self.speed

        self.prevColDir = self.collisionDir

        super().update(delta, tilemap, colRects)

    def keydown(self, event):
        if event.key == pygame.K_w:
            if self.collisionDir & 0b0010 > 0:
                self.vel.y = -self.jumpHeight