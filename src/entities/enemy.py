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

            self.kicked = False

            self.decoratorObj = cls(self, **kwargs)

            if hasattr(self.decoratorObj, "collide"):
                self.collide = self.childCollide
            else:
                self.collide = self.internalCollide 

        def internalCollide(self, rect):
            return self.rect.colliderect(rect)

        def childCollide(self, rect):
            return self.decoratorObj.collide(self.rect, rect)
    
        def stun(self, time):
            self.stunTimer = time
        
        def kick(self, vel):
            self.stunTimer = 0
            self.kicked = True
            self.vel.x = vel

        # Return whether or not it is alive
        def damage(self, amt):
            if self.damageTimer <= 0:
                self.health -= amt
                self.damageTimer = 0.5
            return self.health > 0
        
        def draw(self, win, scroll):
            if self.health != self.maxHealth:
                r = pygame.Rect(self.pos.x - scroll.x, self.pos.y - self.height/2 - scroll.y, self.width, self.height/4)
                pygame.draw.rect(win, (255,0,0), r)
                pygame.draw.rect(win, (0,255,0), (r.x, r.y, r.w * (self.health/self.maxHealth), r.h))
            self.decoratorObj.draw(win, self, scroll)
        
        def update(self, delta, player, tilemap=None, colRects=None):
            if self.stunTimer <= 0:
                if self.kicked:
                    self.vel.x *= 0.9
                    if abs(self.vel.x) < 10: self.kicked = False
                else:
                    self.decoratorObj.update(delta, self, player, tilemap)
                super().update(delta, tilemap, colRects)
            else:
                self.stunTimer -= delta
                
            if self.damageTimer > 0:    self.damageTimer -= delta
    return EnemyWrapper

@enemy
class FlyingEnemy:
    # No states, dumb enemy

    class Projectile:
        def __init__(self, pos, target, r=2):
            self.pos = pos

            speed = 16*6

            dirVec = target - pos
            self.vel = speed * dirVec.normalize()
            #self.angle = math.atan2(dirVec.y, dirVec.x)

            self.r = r
        
        def draw(self, win, scroll):
            pygame.draw.rect(win, (255,255,255), (self.pos.x-self.r-scroll.x, self.pos.y-self.r-scroll.y, self.r+self.r, self.r+self.r))
        
        def update(self, delta):
            self.pos += self.vel * delta

    def __init__(self, enemy):
        enemy.applyGravity = False

        self.angle = 0
        self.shootRate = 0.75
        self.shootTimer = self.shootRate

        self.speed = 16 * 3

        self.projectiles = []
    
    def collide(self, r1, r2):
        for proj in self.projectiles:
            if r2.collidepoint(proj.pos):  return True
        return r1.colliderect(r2)
    
    def draw(self, win, enemy, scroll):
        pygame.draw.rect(win, (0,255,0), (enemy.pos.x - scroll.x, enemy.pos.y - scroll.y, enemy.width, enemy.height), 1)
        for proj in self.projectiles:
            proj.draw(win, scroll)
    
    def update(self, delta, enemy, player, tilemap):
        self.angle += 3 * delta
        self.angle = math.fmod(self.angle, math.tau)

        enemy.vel.x = math.sin(self.angle) * self.speed
        enemy.vel.y = math.cos(self.angle) * self.speed

        self.shootTimer -= delta
        if self.shootTimer <= 0:
            self.shootTimer = self.shootRate
            self.projectiles.append(self.Projectile(enemy.center, player.center))

        for i in range(len(self.projectiles))[::-1]:
            self.projectiles[i].update(delta)
            if tilemap.collidePoint(self.projectiles[i].pos):
                self.projectiles.pop(i)

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

    def update(self, delta, enemy, player, tilemap):
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
        if self.currentState != self.States.ATTACK and (enemy.damageTimer > 0 or enemy.center.distance_squared_to(player.center) < 2500): # radius - 50
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

    def update(self, delta, enemy, player, tilemap):
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

        if self.currentState != self.States.ATTACK and (enemy.damageTimer > 0 or enemy.center.distance_squared_to(player.center) < 2500): # radius - 50
            self.changeState(self.States.ATTACK, enemy)

    def changeState(self, newState, enemy):
        enemy.vel.x = 0
        if newState != self.States.ATTACK:
            self.dir = (self.dir > 0) * 2 - 1
            self.searchTimer = 2

        self.currentState = newState