import pygame
from pygame.math import Vector2

import json

class Tilemap:
    def __init__(self, tileSize, imgs, chunkSize=8):
        self.tileSize = tileSize
        self.imgs = imgs
        self.drawTiles = []
        self.chunks = {}
        self.chunkSize = chunkSize

    def getColRects(self, rect, vel):
        toChunkPos = lambda p:int(p/self.tileSize/self.chunkSize)
        
        testPointsX = (
            rect.x,
            rect.right,
            rect.x + vel.x,
            rect.right + vel.x
        )
        minX = toChunkPos(min(testPointsX))
        maxX = toChunkPos(max(testPointsX))

        testPointsY = (
            rect.y,
            rect.bottom,
            rect.y + vel.y,
            rect.bottom + vel.y
        )
        minY = toChunkPos(min(testPointsY))
        maxY = toChunkPos(max(testPointsY))

        testChunkPositions = {
            (minX, minY), (minX, maxY),
            (maxX, minY), (maxX, maxY)
        }

        out = []
        for pos in testChunkPositions:
            if pos in self.chunks:
                out += self.chunks[pos]
        return out
        
    def draw(self, win, scroll=None):
        if scroll is None:    scroll = Vector2(0, 0)
        for layer in self.drawTiles:
            for tile in layer:
                win.blit(self.imgs[tile[2]], \
                    (tile[0] * self.tileSize - scroll.x, tile[1] * self.tileSize - scroll.y))

    def drawCollision(self, win, scroll=None):
        if scroll is None:    scroll = Vector2(0, 0)
        cols = ((255,0,0), (0,255,0), (0,0,255))
        for pos, rects in self.chunks.items():
            for i, rect in enumerate(rects):
                pygame.draw.rect(win, cols[i%len(cols)], \
                (rect.x - scroll.x, rect.y - scroll.y, \
                 rect.w, rect.h), width=1)

    def loadLevel(self, filepath):
        with open(filepath, 'r') as f:
            data = json.loads(f.read())
        for layer in data["drawTiles"]:
            tempLayer = []
            for key, item in layer.items():
                pStr = key.split(';')
                x, y = int(pStr[0]), int(pStr[1])
                tempLayer.append((x, y, item))
            self.drawTiles.append(tempLayer)

        for pos, rects in data["chunks"].items():
            tempRects = []
            for rect in rects:
                tempRects.append(pygame.Rect(rect))
            pStr = pos.split(';')
            self.chunks[(int(pStr[0]), int(pStr[1]))] = tempRects