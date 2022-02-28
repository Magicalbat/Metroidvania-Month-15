import pygame
from pygame.math import Vector2

class Entity:
    def __init__(self, x, y, w, h):
        self.pos = Vector2(x, y)
        self.width, self.height = w, h

        self.vel = Vector2(0, 0)

        self.applyGravity = False
        self.applyVelocity = False
        self.applyCollision = False

    @property
    def clampedPos(self):
        out = Vector2()
        