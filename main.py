import pygame
from pygame.math import Vector2

from src.common import loadSpriteSheet
from src.tilemap import Tilemap

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
    tilemap.loadLevel("res/levels/testlevel.json")

    pos = Vector2(0,0)
    scroll = Vector2(0,0)

    running = True
    while running:
        clock.tick(fps)
        delta = clock.get_time() / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        speed = 50
        if keys[pygame.K_w]:    pos.y -= speed * delta
        if keys[pygame.K_s]:    pos.y += speed * delta
        if keys[pygame.K_d]:    pos.x += speed * delta
        if keys[pygame.K_a]:    pos.x -= speed * delta

        scroll += ((pos-Vector2(width/2, height/2)) - scroll) / 10

        win.fill((200,200,200))

        tilemap.draw(win, scroll)

        pygame.draw.circle(win, (0,245,255), pos-scroll, 5)

        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()
