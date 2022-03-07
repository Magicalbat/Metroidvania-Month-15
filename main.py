import pygame
from pygame.math import Vector2

from src.screens.screenmanager import ScreenManager
from src.screens.level import Level 

def main():
    pygame.init()

    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])

    width = 320
    height = 180
    win = pygame.display.set_mode((width, height), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption('Metroidvania Month 15')

    clock = pygame.time.Clock()
    fps = 60

    screenManager = ScreenManager(Level("res/levels/cameratest.json"))
    
    running = True
    while running:
        clock.tick(fps)
        delta = min(clock.get_time() / 1000, 0.1)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                screenManager.keydown(event)
            if event.type == pygame.KEYUP:
                screenManager.keyup(event)

        screenManager.update(delta)

        win.fill((200,200,200))

        screenManager.draw(win)

        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()