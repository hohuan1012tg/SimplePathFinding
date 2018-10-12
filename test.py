import pygame 
WINDOW_SIZE = [500,500]
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("A* Search")
AQUA = (0, 255, 255)
pygame.draw.circle(screen, AQUA, (0,0), 50)
pygame.display.flip()