import pygame
from pygame.math import Vector2

import math

from src.entities.entity import Entity

class Player(Entity):
    def __init__(self, *args):
        super().__init__(*args)

        self.speed = 16*5
        self.jumpHeight = 150

        self.applyGravity, self.applyCollision = True, True

        maxJumpHeight = 3.35 * 16
        minJumpHeight = 0.5 * 16

        self.maxJumpVel = -math.sqrt(2 * self.gravity * maxJumpHeight)
        self.minJumpVel = -math.sqrt(2 * self.gravity * minJumpHeight)
        
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
                self.vel.y = self.maxJumpVel

    def keyup(self, event):
        if event.key == pygame.K_w:
            if self.vel.y < self.minJumpVel:
                self.vel.y = self.minJumpVel