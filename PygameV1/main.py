#import libraries
import pygame as pg
from datetime import datetime

#initialise pygame
pg.init()

#game window
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800
clock = pg.time.Clock()
FPS = 60
scroll = 0

#create game window
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))



def logging(Funktion, Datei):
    uhrzeit = datetime.now().strftime("%H:%M:%S")
    log = f"{uhrzeit} :{Funktion} - {Datei} erfolgreich ausgeführt.\n"
    with open("Debug Log.txt" ,'a') as file:
          file.write(log)
       

#load images
ground_image = pg.image.load("assets/Background/ground.png").convert_alpha()
ground_width = ground_image.get_width()
ground_height = ground_image.get_height()
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
            screen.blit(ground_image,((x * ground_width) - scroll * 2.5, 0)) 
            logging("draw_ground",x)
            


    def draw_bg():
        for i in bg_images:
            for x in range(6):
                screen.blit(i,((x * bg_width) - scroll * 2.5, 0))
                logging("draw_bg",{bg_image})
            

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


#game loop
run = True
while run:
	framerate = int(clock.get_fps())
	pg.display.set_caption(f"Running at {framerate} fps.")
	clock.tick(FPS)
	Background.draw_bg()
	Background.draw_ground()
	#draw castle
	castle.draw()
	pg.display.update()
	#event handler
	for event in pg.event.get():
		if event.type == pg.QUIT:
			run = False
    
	
	

pg.quit()