import pygame
from pygame.math import Vector2

import math

from src.entities.entity import Entity
from src.utils.particles import Particles

class Player(Entity):
    def __init__(self, *args):
        super().__init__(*args)

        self.speed = 16*5

        self.applyGravity, self.applyCollision = True, True

        maxJumpHeight = 3.35 * 16
        minJumpHeight = 0.5 * 16

        self.maxJumpVel = -math.sqrt(2 * self.gravity * maxJumpHeight)
        self.minJumpVel = -math.sqrt(2 * self.gravity * minJumpHeight)

        self.waterParticles = Particles((3,5), (-.1,.1,-.1,.1), circle=True, speed=5, accel=Vector2(0, self.gravity), collision=True, colors=[
            (0,0,255), (0,0,225), (0,0,200),
            (0,245,255), (0,128,255), (0,225,225),
        ])

        self.dir = 1

        self.acid = False
        self.kickReady = False

    def enableAcid(self):
        self.acid = True
        self.waterParticles.clear()
        self.waterParticles.colors = [
            (0,255,0), (0,225,0), (0,220,100)
        ]

    def draw(self, win, scroll):
        pygame.draw.rect(win, (0,245,255), (self.pos - scroll, (self.width, self.height)))
        #super().draw(win, scroll)
        self.waterParticles.draw(win, scroll)

    def update(self, delta, tilemap=None, colRects=None):
        self.waterParticles.update(delta, tilemap)
        
        keys = pygame.key.get_pressed()

        self.vel.x *= 0.85

        left, right = keys[pygame.K_LEFT], keys[pygame.K_RIGHT]
        if left:
            self.vel.x -= 12
            self.vel.x = max(self.vel.x, -self.speed)
            self.dir = -1
        if right:
            self.vel.x += 12
            self.vel.x = min(self.vel.x, self.speed)
            self.dir = 1
            
        if self.kickReady:
            if keys[pygame.K_DOWN]:
                r = pygame.Rect(self.pos.x, self.pos.y + self.height, self.width, self.height/2)
                if r.collidelist(tilemap.getRectColRects(r)) != -1:
                    self.kickReady = False
                    self.vel.y = -750
            elif right or left:
                r = pygame.Rect(self.pos.x + self.width*self.dir, self.pos.y, self.width, self.height)
                if r.collidelist(tilemap.getRectColRects(r)) != -1:
                    self.kickReady = False
                    self.vel.x = 750 * -self.dir

        if keys[pygame.K_x]:
            if self.dir < 0:
                self.waterParticles.emit(self.rect.midleft, 1, (self.vel.x, -200+self.vel.x, -10, -90))
            else:
                self.waterParticles.emit(self.rect.midright, 1, (self.vel.x, 200+self.vel.x, -10, -90))

        super().update(delta, tilemap, colRects)

    def keydown(self, event):
        if event.key == pygame.K_c:
            if self.collisionDir & 0b0010 > 0:
                self.vel.y = self.maxJumpVel

        if event.key == pygame.K_z:
            self.kickReady = True

    def keyup(self, event):
        if event.key == pygame.K_c:
            if self.vel.y < self.minJumpVel:
                self.vel.y = self.minJumpVel

        if event.key == pygame.K_z:
            self.kickReady = False