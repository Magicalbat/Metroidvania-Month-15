import pygame
from pygame.math import Vector2

from src.utils.common import loadSpriteSheet
from src.entities.enemy import *
from src.entities.boss import Boss

class EnemyManager:
    enemyTypes = {
        "GroundEnemies": GroundEnemy,
        "JumpingEnemies": JumpingEnemy,
        "FlyingEnemies": FlyingEnemy,
        "SlowEnemies": SlowEnemy
    }
    enemyImgs = {
        "GroundEnemies": (9, 12), 
        "JumpingEnemies": (6, 9),
        "FlyingEnemies": (3, 6),
        "SlowEnemies": (0, 3)
    }
    def __init__(self, extraData):
        self.enemySpawns = {}

        for enemyType in ["GroundEnemies", "JumpingEnemies", "FlyingEnemies", "SlowEnemies"]:
            if enemyType in extraData:
                self.enemySpawns[enemyType] = extraData[enemyType]
        
        if "Boss" in extraData:
            self.enemySpawns["Boss"] = extraData["Boss"][0]
        if "BossDamagePoints" in extraData:
            self.bossDamagePoints = extraData["BossDamagePoints"]
        
        self.imgs = loadSpriteSheet("res/imgs/enemies.png", (16,16), (3,4), (1,1), 12, (0,0,0))

    def setup(self):
        self.reset = False
        
        self.boss = None
        self.enemies = []
        for enemyType, positions in self.enemySpawns.items():
            if enemyType != "Boss":
                for pos in positions:
                    self.enemies.append(self.enemyTypes[enemyType](pos, 12, 16, \
                        images=self.imgs[self.enemyImgs[enemyType][0]:self.enemyImgs[enemyType][1]]))
            else:
                self.boss = Boss(positions, 12, 16, images=self.imgs[0:3])
        
        self.bossDamageRects = [pygame.Rect(pos, (16, 16)) for pos in self.bossDamagePoints]
        self.bossDamageProgress = [16 for _ in self.bossDamageRects]

    def draw(self, win, scroll):
        if self.boss is not None:
            self.boss.draw(win, scroll)

        for enemy in self.enemies:
            #if screenRect.colliderect(enemy.rect):
            enemy.draw(win, scroll)
        
        for p, r in zip(self.bossDamageProgress, self.bossDamageRects):
            w = (p/16) * 6
            pygame.draw.rect(win, (0,200,50), (r.centerx-scroll.x-w*0.5, r.y-scroll.y, w, 5))
            pygame.draw.circle(win, (255,50,50), (r.x-scroll.x+r.w*0.5, r.y-scroll.y+5+r.w*0.5), r.w*0.5)

    def update(self, delta, tilemap, player, screenRect, playerSpawn=(0,0)):
        if self.boss is not None:
            self.boss.update(delta, tilemap, player)
            if self.boss.spawnEnemy:
                self.boss.spawnEnemy = False
                self.enemies.append(self.enemyTypes[self.boss.enemySpawnType](self.boss.enemySpawnPos, 12, 16, \
                    images=self.imgs[self.enemyImgs[self.boss.enemySpawnType][0]:self.enemyImgs[self.boss.enemySpawnType][1]]))
                dir = self.boss.enemySpawnDir
                self.enemies[-1].decoratorObj.dir = dir
                self.enemies[-1].vel.x = self.enemies[-1].decoratorObj.getCurrentSpeed() * dir

            if not player.invincible:
                if self.boss.collide(player.rect):
                    self.reset = True

            if player.acid:
                if player.waterParticles.collideRect(self.boss.rect):
                    origPhase = self.boss.phase
                    if not self.boss.damage(1):
                        self.boss = None
                        self.bossDamagePoints = []
                    if self.boss is not None and self.boss.phase != origPhase:
                        player.pos = Vector2(playerSpawn)
                        player.updateRectPos()
                for i in range(len(self.bossDamageProgress))[::-1]:
                    if player.waterParticles.collideRect(self.bossDamageRects[i]):
                        self.bossDamageProgress[i] -= 0.25
                        if self.bossDamageProgress[i] < 3:
                            self.bossDamageRects.pop(i)
                            self.bossDamageProgress.pop(i)

                            player.pos = Vector2(playerSpawn)
                            player.updateRectPos()

                            self.boss.invincible = False

        for enemy in self.enemies:
            enemy.onScreen = enemy.rect.colliderect(screenRect)
            enemy.update(delta, player, tilemap)

        for i in range(len(self.enemies))[::-1]:
            if self.enemies[i].onScreen:#screenRect.colliderect(self.enemies[i].rect):
                if player.waterParticles.collideRect(self.enemies[i].rect):
                    if player.acid:
                        if not self.enemies[i].damage(1):
                            self.enemies.pop(i)
                    else:
                        self.enemies[i].stun(1)

        if not player.invincible:
            for enemy in self.enemies:
                if enemy.stunTimer <= 0 and enemy.collide(player.rect):#rect(player.rect):
                    self.reset = True

    def getStunnedRects(self):
        return [enemy.rect for enemy in self.enemies if enemy.stunTimer > 0]