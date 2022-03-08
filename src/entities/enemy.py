import pygame
from pygame.math import Vector2

import math
from enum import Enum

from src.entities.entity import Entity
from src.utils.common import lerp

def enemy(cls):
    class EnemyWrapper(Entity):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
    
            self.applyGravity, self.applyCollision = True, True
            
            self.stunTimer = 0
            self.damageTimer = 0
            self.maxHealth = 5
            self.health = self.maxHealth

            self.decoratorObj = cls(self, **kwargs)
    
        def stun(self, time):
            self.stunTimer = time

        # Return whether or not it is alive
        def damage(self, amt):
            if self.damageTimer <= 0:
                self.health -= amt
                self.damageTimer = 0.5
            return self.health > 0
        
        def draw(self, win, scroll):
            r = pygame.Rect(self.pos.x - scroll.x, self.pos.y - self.height/2 - scroll.y, self.width, self.height/4)
            pygame.draw.rect(win, (255,0,0), r)
            pygame.draw.rect(win, (0,255,0), (r.x, r.y, r.w * (self.health/self.maxHealth), r.h))
            self.decoratorObj.draw(win, self, scroll)
        
        def update(self, delta, player, tilemap=None, colRects=None):
            if self.stunTimer <= 0:
                self.decoratorObj.update(delta, self, player)
                super().update(delta, tilemap, colRects)
            else:
                self.stunTimer -= delta
                
            if self.damageTimer > 0:    self.damageTimer -= delta
    return EnemyWrapper

@enemy
class JumpingEnemy:
    class States(Enum):
        IDLE = 0
        ATTACK = 1

    def __init__(self, enemy):
        self.currentState = self.States.IDLE

        idleJumpHeight = 16 * 1.2
        attackJumpHeight = 16 * 3.2

        self.idleJumpVel = -math.sqrt(2 * enemy.gravity * idleJumpHeight)
        self.attackJumpVel = -math.sqrt(2 * enemy.gravity * attackJumpHeight)

        self.idleSpeed = 16 * 2
        self.attackSpeed = 16 * 5

        self.dir = -1

    def draw(self, win, enemy, scroll):
        col = (0,255,0)
        if self.currentState == self.States.ATTACK:    col = (255,0,0)
        pygame.draw.rect(win, col, pygame.Rect(enemy.pos - scroll, (enemy.width, enemy.height)), 1)

    def update(self, delta, enemy, player):
        if enemy.collisionDir & 0b0010 > 0:
            if self.currentState == self.States.IDLE:
                self.dir *= -1
                enemy.vel.x = self.idleSpeed  * self.dir
                enemy.vel.y = self.idleJumpVel
            elif self.currentState == self.States.ATTACK:
                enemy.vel.x = self.attackSpeed  * self.dir
                enemy.vel.y = self.attackJumpVel

        if self.currentState == self.States.ATTACK:
            self.dir = ((enemy.pos.x + enemy.width*0.5) < (player.pos.x + player.width*0.5)) * 2 - 1
            if abs(player.pos.x - enemy.pos.x) < 10:
                if player.vel.length() < 0.1:    enemy.vel.x *= 0.9
                else:    enemy.vel.x *= 0.96

        # To attack
        if self.currentState != self.States.ATTACK and enemy.center.distance_squared_to(player.center) < 2500: # radius - 50
            self.changeState(self.States.ATTACK, enemy)

        # Out of attack
        if self.currentState == self.States.ATTACK and enemy.center.distance_squared_to(player.center) > 10000: # radius - 100
            self.changeState(self.States.IDLE, enemy)

    def changeState(self, newState, enemy):
        self.currentState = newState

@enemy
class GroundEnemy:
    class States(Enum): 
        PATROL = 0
        ATTACK = 1
        SEARCH = 2
        
    def __init__(self, enemy):
        self.currentState = self.States.PATROL

        self.walkSpeed = 16 * 3
        self.runSpeed  = 16 * 4.5
        self.dir = 1
        self.searchTimer = 0
    
    def draw(self, win, enemy, scroll):
        col = (0,255,0)
        if self.currentState == self.States.ATTACK: col = (255,0,0)
        if self.currentState == self.States.SEARCH: col = (0,0,255)
        pygame.draw.rect(win, col, pygame.Rect(enemy.pos - scroll, (enemy.width, enemy.height)), 1)

    def update(self, delta, enemy, player):
        if self.currentState == self.States.PATROL:
            if enemy.collisionDir & 0b0100 > 0 or enemy.collisionDir & 0b0001 > 0:
                self.dir *= -1
            enemy.vel.x = self.walkSpeed * self.dir
        elif self.currentState == self.States.ATTACK:
            self.dir = lerp(self.dir, ((enemy.pos.x + enemy.width*0.5) < (player.pos.x + player.width*0.5)) * 2 - 1, 0.05)
            enemy.vel.x = self.runSpeed * self.dir

            if enemy.center.distance_squared_to(player.center) > 15625: # radius - 125
                self.changeState(self.States.SEARCH, enemy)
        elif self.currentState == self.States.SEARCH:
            enemy.vel.x = self.runSpeed * self.dir

            self.searchTimer -= delta
            if self.searchTimer < 0:
                self.changeState(self.States.PATROL, enemy)

        if self.currentState != self.States.ATTACK and enemy.center.distance_squared_to(player.center) < 2500: # radius - 50
            self.changeState(self.States.ATTACK, enemy)

    def changeState(self, newState, enemy):
        enemy.vel.x = 0
        if newState != self.States.ATTACK:
            self.dir = (self.dir > 0) * 2 - 1
            self.searchTimer = 2

        self.currentState = newState