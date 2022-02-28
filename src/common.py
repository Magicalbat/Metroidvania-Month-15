import pygame

def loadSpriteSheet(imgPath, spriteSize, dim, padding, count, colorKey=None):
    mainImg = pygame.image.load(imgPath).convert()

    if colorKey is not None:
        mainImg.set_colorkey(colorKey, pygame.RLEACCEL)
    
    imgs = []

    i = 0
    for y in range(dim[1]):
        for x in range(dim[0]):
            rect = pygame.Rect(x * (spriteSize[0] + padding[0]), y * (spriteSize[0] + padding[1]), spriteSize[0], spriteSize[1])
            
            rect.right = min(rect.right, mainImg.get_width())
            rect.bottom = min(rect.bottom, mainImg.get_height())

            imgs.append(mainImg.subsurface(rect))

            i += 1

            if i > count - 1:
                return imgs
    
    return imgs
