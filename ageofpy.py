import pygame
from pygame.locals import *
from OpenGL.GL import *
from systems.renderer import *

def init_display():
    pygame.init()
    pygame.display.set_mode((1600, 1000), DOUBLEBUF | OPENGL)
    glOrtho(0, 1600, 1000, 0, -2, 3)  # 2D-Kamera: oben links = (0,0)

def main():
    init_display()
    soldier_texture, w, h = load_texture("assets/soldier.png")

    x = 0
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT)

        draw_sprite(x, 500, w, h, soldier_texture)

        pygame.display.flip()
        clock.tick(60)
        x += 1  # Bewegung nach rechts

    pygame.quit()

if __name__ == "__main__":
    main()
