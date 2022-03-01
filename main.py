import pygame
from pygame.math import Vector2

from src.common import loadSpriteSheet
from src.tilemap import Tilemap
from src.entity import Entity

def main():
    pygame.init()

    pygame.event.set_allowed([pygame.QUIT])

    width = 320
    height = 180
    win = pygame.display.set_mode((width, height), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption('Metroidvania Month 15')

    clock = pygame.time.Clock()
    fps = 60

    images = loadSpriteSheet("res/temptiles.png", (16,16), (3,1), (1,1), 3, (0,0,0))
    tilemap = Tilemap(16, images)
    extraData = tilemap.loadLevel("res/levels/testlevel.json")
    
    e = Entity(40, 40, 12, 20)
    e.applyGravity = True
    e.applyCollision = True
    e.pos.x = extraData["PlayerSpawn"][0][0]
    e.pos.y = extraData["PlayerSpawn"][0][1] - e.height
    
    scroll = Vector2(0,0)

    running = True
    while running:
        clock.tick(fps)
        delta = clock.get_time() / 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        e.vel.x = 0
        if keys[pygame.K_d]:    e.vel.x =  50
        if keys[pygame.K_a]:    e.vel.x = -50
            
        e.update(delta, tilemap)
            
        scroll += ((e.center-Vector2(width/2, height/2)) - scroll) / 10

        win.fill((200,200,200))

        tilemap.draw(win, scroll)
        tilemap.drawCollision(win, scroll)

        e.draw(win, scroll)

        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()
