import pygame
from pygame.math import Vector2

from enum import Enum

from src.entities.entity import Entity

# https://levelup.gitconnected.com/mastering-decorators-in-python-3-588cb34fff5e

def enemy(cls):
    class EnemyWrapper(Entity):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
    
            self.applyGravity, self.applyCollision = True, True
            
            self.stunTimer = 0

            self.decoratorObj = cls(**kwargs)
    
        def stun(self, time):
            self.stunTimer = time
        
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

        self.speed = 16 * 5
        self.dir = 1

    def update(self, delta, enemy, player):
        if self.curretnState == self.States.PATROL:
            if enemy.collisionDir & 0b0100 > 0 or enemy.collisionDir & 0b0001 > 0:
                self.dir *= -1
        enemy.vel.x = self.speed * self.dir

    def changeState(self, newState):
        pass