#import libraries
import pygame as pg
from datetime import datetime
import sys
from pygame.locals import *
import multiprocessing

#initialise pygame
pg.init()

#game window
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800
clock = pg.time.Clock()
FPS = 60
scroll = 0
window_num = 2
font = pg.font.SysFont(None, 30)

#create game window
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), RESIZABLE)

fullscreen = False



def logging(Funktion, Datei):
    uhrzeit = datetime.now().strftime("%H:%M:%S")
    log = f"{uhrzeit} :{Funktion} - {Datei} erfolgreich ausgeführt.\n"
    with open("Debug Log.txt" ,'a') as file:
          file.write(log)
       

#load images
GroundImageBase = pg.image.load("assets/Background/ground.png").convert_alpha()
ground_width = GroundImageBase.get_width()
ground_height = GroundImageBase.get_height()
bg_images = []
for i in range(1, 4):
         bg_image = pg.image.load(f"assets/Background/{i}.png").convert_alpha()
         bg_images.append(bg_image)
         bg_width = bg_images[0].get_width()
         bg_height = bg_images[0].get_height()
         

#castle
castle_img_100 = pg.image.load('assets/castle/castle_100.png').convert_alpha()

class Background():

    

    def draw_ground():
        for x in range(5):
            screen.blit(GroundImageBase,((x * ground_width) - scroll * 2.5, 0)) 
            #logging("draw_ground",x)
            
 

    def draw_bg():
        for i in bg_images:
            for x in range(6):
                screen.blit(i,((x * bg_width) - scroll * 2.5, 0))
                #logging("draw_bg",{bg_image})
            

#castle class
class Castle():
	def __init__(self, image100, x, y, scale):
		self.health = 1000
		self.max_health = self.health

		width = image100.get_width()
		height = image100.get_height()

		self.image100 = pg.transform.scale(image100, (int(width * scale), int(height * scale)))
		self.rect = self.image100.get_rect()
		self.rect.x = x
		self.rect.y = y


	def draw(self):
		self.image = self.image100

		screen.blit(self.image, self.rect)



#create castle
castle = Castle(castle_img_100, SCREEN_WIDTH - 250, SCREEN_HEIGHT - 300, 0.2)


def draw_text(text, font, color, surface, x, y):
      textobj = font.render(text, 1, color)
      textrect = textobj.get_rect()
      textrect.topleft = (x, y)
      surface.blit(textobj, textrect)


click = False

def main_menu():
      while True:
            framerate = int(clock.get_fps())
            (ActiveWIDTH, ActiveHEIGHT) = pg.display.get_window_size()
            (ScaleX, ScaleY) = SCREEN_WIDTH/ActiveWIDTH, SCREEN_HEIGHT/ActiveHEIGHT
            pg.display.set_caption(f"Running at {framerate} fps in {ActiveWIDTH}x{ActiveHEIGHT}")
            mx, my = pg.mouse.get_pos()
            screen.fill((0,0,0))
            draw_text("main menu", font, (255, 255 ,255), screen, 20, 20)
            Background.draw_bg()
            Background.draw_ground()
            button_1 = pg.Rect(ActiveWIDTH/2, ActiveHEIGHT/2, 100, 50)
            button_2 = pg.Rect(ActiveWIDTH/2, ActiveHEIGHT/2+100, 100, 50)
            if button_1.collidepoint((mx, my)):
                  if click:
                    game()
                        
                
            if button_2.collidepoint((mx, my)):
                  if click:
                     options()
            
            pg.draw.rect(screen, (255, 0, 0), button_1)
            pg.draw.rect(screen, (255, 0, 0), button_2)
            
            click = False
            for event in pg.event.get():
             if event.type == QUIT:
                 pg.quit()
                 sys.exit()
             if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                     pg.quit()
                     sys.exit()
             if event.type == MOUSEBUTTONDOWN:
                     click = True
 
             pg.display.update()
             clock.tick(FPS)

            

def game():
    running = True
    while running:
        screen.fill((0,0,0))
        Background.draw_bg()
        Background.draw_ground()
        castle.draw()
        draw_text('game', font, (255, 255, 255), screen, 20, 20)
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        pg.display.update()
        clock.tick(FPS)
        

def options():
    running = True
    while running:
        screen.fill((0,0,0))
        Background.draw_bg()
        Background.draw_ground()
        draw_text('options', font, (255, 255, 255), screen, 20, 20)
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        pg.display.update()
        clock.tick(FPS)
if __name__ == '__main__':
    for _ in range(window_num):
        multiprocessing.Process(target=main_menu).start()
        main_menu()

#game loop
#run = True
#while run:
#	framerate = int(clock.get_fps())
#	pg.display.set_caption(f"Running at {framerate} fps.")
#	clock.tick(FPS)
#	Background.draw_bg()
#	Background.draw_ground()
#	#draw castle
#	castle.draw()
#	pg.display.update()
#	#event handler
#	for event in pg.event.get():
#		if event.type == pg.QUIT:
#			run = False
#		if event.type == MOUSEBUTTONDOWN:
#			pass

