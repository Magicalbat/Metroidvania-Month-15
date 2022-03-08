import pygame
from pygame.math import Vector2

import math

class Entity:
    def __init__(self, *args):
        if len(args) == 4 or len(args) == 1:    x, y, w, h = args
        elif len(args) == 3:    (x, y), w, h = args
        elif len(args) == 2:    (x, y), (w, h) = args
        else:    print(f"Invalid args: {args}")
            
        self.pos = Vector2(x, y)
        self.width, self.height = w, h

        self.vel = Vector2(0, 0)

        # UP RIGHT DOWN LEFT
        self.collisionDir = 0b0000

        self.gravity = 430

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

    @property
    def center(self):
        return self.pos + Vector2(self.width * 0.5, self.height * 0.5)

    def update(self, delta, tilemap=None, colRects=None):
        if self.applyGravity:
            self.vel.y += self.gravity * delta
        if self.applyCollision:
            if colRects is None:    colRects = []
            if tilemap is not None:
                tilemap.getEntityColRects(self.pos, self.width, self.height, self.vel * delta, colRects)

            self.collisionDir = 0b0000
            
            self.pos.x += self.vel.x * delta
            indices = self.rect.collidelistall(colRects)

            for i in indices:
                if self.vel.x > 0:
                    self.pos.x = colRects[i].x - self.width
                    self.vel.x = 0
                    self.collisionDir |= 0b0100
                elif self.vel.x < 0:
                    self.pos.x = colRects[i].right
                    self.vel.x = 0
                    self.collisionDir |= 0b0001

            self.pos.y += self.vel.y * delta
            indices = self.rect.collidelistall(colRects)

            for i in indices:
                if self.vel.y > 0:
                    self.pos.y = colRects[i].y - self.height
                    self.vel.y = 0
                    self.collisionDir |= 0b0010
                elif self.vel.y < 0:
                    self.pos.y = colRects[i].bottom
                    self.vel.y = 0
                    self.collisionDir |= 0b1000
            
        elif self.applyVelocity:
            self.pos += self.vel * delta

    def collideEntities(self, entities):
        rect = self.rect
        for e in entities:
            if rect.colliderect(e.rect):    return True
        return False

    def draw(self, win, scroll):
        pygame.draw.rect(win, (255,0,0), pygame.Rect(self.clampedPos - scroll, (self.width, self.height)), 1)