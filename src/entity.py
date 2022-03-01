import pygame
from pygame.math import Vector2

import math

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
        out.x = math.ceil(self.pos.x) if self.vel.x > 0 else int(self.pos.x)
        out.y = math.ceil(self.pos.y) if self.vel.y > 0 else int(self.pos.y)
        return out

    @property
    def rect(self):
        return pygame.Rect(self.clampedPos, (self.width, self.height))

    def draw(self, win, scroll):
        pygame.draw.rect(win, (255,0,0), pygame.Rect(self.clampedPos - scroll, (self.width, self.height)), 1)