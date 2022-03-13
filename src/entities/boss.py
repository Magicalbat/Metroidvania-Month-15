import pygame
from pygame.math import Vector2

from src.entities.entity import Entity
from src.utils.animation import Animation

class Boss(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.applyGravity, self.applyCollision = True, True

        self.speed = 16 * 3.5
        self.dir = -1

        self.vel.x = self.speed * self.dir

        self.imgs = kwargs["images"]
        self.anim = Animation([1, 3], 4, realTime=True)

        self.phase = 0
        self.healths = [5, 15, 25]
        self.health = self.healths[self.phase]
        self.damageTimer = 0
    
    # Return whether or not it is alive
    def damage(self, amt):
        if self.damageTimer <= 0:
            self.health -= amt
            self.damageTimer = 0.5
        if self.health <= 0:
            self.phase += 1
            if self.phase >= len(self.healths): return False
            self.health = self.healths[self.phase]

            self.pos.x -= self.width
            self.pos.y -= self.height
            self.width *= 2
            self.height *= 2
            self.updateRect()
        return True
    
    def draw(self, win, scroll):
        if self.phase == 0:
            if self.health != self.healths[self.phase]:
                r = pygame.Rect(self.pos.x - scroll.x, self.pos.y - self.height/2 - scroll.y, self.width, self.height/4)
            else:
                r = pygame.Rect(0, 0, 0, 0)
        else:
            r = pygame.Rect(40, 2, 240, 5)
        pygame.draw.rect(win, (255,0,0), r)
        pygame.draw.rect(win, (0,255,0), (r.x, r.y, r.w * (self.health/self.healths[self.phase]), r.h))
        drawIndex = int(self.anim.value)
        if self.collisionDir & 0b0010 == 0: drawIndex = 0

        scale = 2**self.phase
        win.blit(pygame.transform.scale(pygame.transform.flip(self.imgs[drawIndex], self.dir == -1, False), (16*scale, 16*scale)), self.pos-scroll+(-2*scale, 0))
        super().draw(win, scroll)
    
    def update(self, delta, tilemap, colRects=None):
        self.anim.update(delta)
        self.damageTimer -= delta
        if self.collisionDir & 0b0100 > 0 or self.collisionDir & 0b0001 > 0:
            self.dir *= -1
            self.vel.x = self.speed * self.dir
            
        super().update(delta, tilemap, colRects)