from hashlib import new
from matplotlib.cbook import Stack
import pygame
from pygame.math import Vector2

from enum import Enum

from src.entities.entity import Entity
from src.utils.common import lerp

def enemy(cls):
    class EnemyWrapper(Entity):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
    
            self.applyGravity, self.applyCollision = True, True
            
            self.stunTimer = 0

            self.decoratorObj = cls(**kwargs)
    
        def stun(self, time):
            self.stunTimer = time
        
        def draw(self, win, scroll):
            self.decoratorObj.draw(win, self, scroll)
        
        def update(self, delta, player, tilemap=None, colRects=None):
            if self.stunTimer <= 0:
                self.decoratorObj.update(delta, self, player)
                super().update(delta, tilemap, colRects)
            else:
                self.stunTimer -= delta
    return EnemyWrapper

@enemy
class GroundEnemy:
    class States(Enum): 
        PATROL = 0
        ATTACK = 1
        SEARCH = 2
        
    def __init__(self):
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
        if newState == self.States.SEARCH:
            self.dir = (self.dir > 0) * 2 - 1
            self.searchTimer = 2

        self.currentState = newState