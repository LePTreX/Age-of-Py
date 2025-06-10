#import libraries
import pygame as pg
from datetime import datetime
import sys, random
from pygame.locals import *

# initialise pygame
pg.init()

# game window
DefaultScreen_Width = 1800
DefaultScreen_Height = 324
clock = pg.time.Clock()
FPS = 60
scroll = 1
font = pg.font.SysFont(None, 30)
#create game window
screen = pg.display.set_mode((DefaultScreen_Width, DefaultScreen_Height))

# globale Währungsvariablen
player_gold = 100
enemy_gold = 100

# load images
button_start = pg.image.load("assets/gfx/button_start.png").convert_alpha()
GroundImageBase = pg.image.load("assets/Background/ground.png").convert_alpha()
ground_width = GroundImageBase.get_width()
ground_height = GroundImageBase.get_height()
bg_images = []
for i in range(1, 4):
    bg_image = pg.image.load(f"assets/Background/{i}.png").convert_alpha()
    bg_images.append(bg_image)
    bg_width = bg_images[0].get_width()
    bg_height = bg_images[0].get_height()
             
# castle image
castle_img_100 = pg.image.load('assets/castle/castle_100.png').convert_alpha()

class Background():
    @staticmethod
    def draw_ground():
        for x in range(5):
            screen.blit(GroundImageBase, ((x * ground_width) - scroll * 2.5, 0))
    @staticmethod
    def draw_bg():
        for i in bg_images:
            for x in range(6):
                screen.blit(i, ((x * bg_width) - scroll * 2.5, 0))

class Castle():
    def __init__(self, image, x, y, scale, team="player"):
        self.team = team
        self.max_health = 1000
        self.health = self.max_health
        width = image.get_width()
        height = image.get_height()
        self.image = pg.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect(topleft=(x, y))
    def draw(self):
        screen.blit(self.image, self.rect)
    def update(self):
        if self.health < 0:
            self.health = 0

def load_sprite_sheet(sheet_path, frame_count, scale=1):
    sheet = pg.image.load(sheet_path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // frame_count
    frames = []
    for i in range(frame_count):
        frame_rect = (i * frame_width, 0, frame_width, sheet_height)
        frame = sheet.subsurface(frame_rect)
        if scale != 1:
            frame = pg.transform.scale(frame, (int(frame_width * scale), int(sheet_height * scale)))
        frames.append(frame)
    return frames

class Troop(pg.sprite.Sprite):
    def __init__(self, animations, x, y, scale=1, team="player"):
        super().__init__()
        self.team = team
        self.animations = {}
        for state, (sheet_path, frame_count) in animations.items():
            if state == "archery":
                continue
            self.animations[state] = load_sprite_sheet(sheet_path, frame_count, scale)
        self.state = 'idle'
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_speed = 100  # ms pro Frame
        
        self.image = self.animations[self.state][self.animation_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.max_health = 100
        self.health = self.max_health
        self.attack_power = 10
        self.attack_range = 50
        self.attack_timer = 0
        self.attack_interval = 1000
        
        if self.team == "enemy":
            self.velocity_x = 30
            self.facing_right = True
        else:
            self.velocity_x = -30
            self.facing_right = False

    def update(self, dt):
        if self.state == 'death':
            self.velocity_x = 0
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                if self.animation_index < len(self.animations['death']) - 1:
                    self.animation_index += 1
            frame = self.animations['death'][self.animation_index]
            self.image = pg.transform.flip(frame, not self.facing_right, False) if not self.facing_right else frame
            return

        if self.velocity_x != 0:
            self.facing_right = (self.velocity_x > 0)
        self.rect.x += self.velocity_x * (dt / 1000.0)
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.animations[self.state])
        frame = self.animations[self.state][self.animation_index]
        self.image = pg.transform.flip(frame, not self.facing_right, False) if not self.facing_right else frame

    def set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.animation_index = 0
            self.animation_timer = 0
            frame = self.animations[self.state][self.animation_index]
            self.image = pg.transform.flip(frame, not self.facing_right, False) if not self.facing_right else frame

class ArcherTroop(Troop):
    def __init__(self, animations, x, y, scale=1, team="player"):
        super().__init__(animations, x, y, scale, team)
        if "archery" in animations:
            self.archery_frames = load_sprite_sheet(animations["archery"][0], animations["archery"][1], scale)
        else:
            self.archery_frames = None
        self.archery_index = 0
        self.archery_timer = 0
        self.archery_speed = 200

    def update(self, dt):
        super().update(dt)
        if self.state == 'attack' and self.archery_frames:
            self.archery_timer += dt
            if self.archery_timer >= self.archery_speed:
                self.archery_timer = 0
                self.archery_index = (self.archery_index + 1) % len(self.archery_frames)
            base_img = self.image.copy()
            bow_frame = self.archery_frames[self.archery_index]
            if not self.facing_right:
                bow_frame = pg.transform.flip(bow_frame, True, False)
            offset_x, offset_y = 10, 5
            base_img.blit(bow_frame, (offset_x, offset_y))
            self.image = base_img

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_health_bar(surface, rect, health, max_health):
    bar_width = rect.width
    bar_height = 5
    fill = (health / max_health) * bar_width
    outline_rect = pg.Rect(rect.x, rect.y - 10, bar_width, bar_height)
    fill_rect = pg.Rect(rect.x, rect.y - 10, fill, bar_height)
    pg.draw.rect(surface, (255, 0, 0), fill_rect)
    pg.draw.rect(surface, (255, 255, 255), outline_rect, 1)

def handle_combat(troop_group, dt, player_castle, enemy_castle):
    global player_gold, enemy_gold
    gold_reward = 10
    dead_troops = []
    
    for troop in troop_group:
        if troop.health <= 0:
            if troop.state != 'death':
                troop.set_state('death')
                troop.velocity_x = 0
            else:
                if troop.animation_index == len(troop.animations['death']) - 1:
                    dead_troops.append(troop)
            continue

        # Standard-Zielauswahl: Bestimme den nächsten Gegner.
        target = None
        min_distance = float('inf')
        for other in troop_group:
            if other.team != troop.team and other.health > 0:
                distance = abs(troop.rect.centerx - other.rect.centerx)
                if distance < min_distance:
                    min_distance = distance
                    target = other
        
        # Falls kein feindlicher Troop gefunden wurde, wähle die Burg als Ziel.
        castle_target = enemy_castle if troop.team == "player" else player_castle
        distance_castle = abs(troop.rect.centerx - castle_target.rect.centerx)
        if distance_castle < min_distance:
            min_distance = distance_castle
            target = castle_target

        # **Neue Bedingung: Einheit greift nur an, wenn der Gegner sich physisch berührt**
        if target and troop.rect.colliderect(target.rect):
            if troop.state != 'attack':
                troop.set_state('attack')
            troop.velocity_x = 0
            troop.attack_timer += dt
            if troop.attack_timer >= troop.attack_interval:
                troop.attack_timer = 0
                target.health -= troop.attack_power
                if hasattr(target, "set_state"):
                    target.set_state('hurt')
        else:
            # Falls kein direkter Gegner da ist, Einheit soll weiterlaufen.
            if troop.state == 'attack':
                troop.set_state('walk')
                troop.velocity_x = 50 if troop.team == "enemy" else -50

    for troop in dead_troops:
        if troop.team == "enemy":
            player_gold += gold_reward
        elif troop.team == "player":
            enemy_gold += gold_reward
        troop_group.remove(troop)


def check_victory_condition(player_castle, enemy_castle):
    if enemy_castle.health <= 0:
        print("Du hast die gegnerische Burg zerstört!")  
        return "player_wins"
    elif player_castle.health <= 0:
        print("Deine Burg wurde zerstört!")  
        return "enemy_wins"
    return None 

def show_end_screen(message):
    screen.fill((0, 0, 0))
    draw_text(message, font, (255, 215, 0), screen, DefaultScreen_Width // 2 - 100, DefaultScreen_Height // 2 - 50)
    pg.display.update()
    pg.time.delay(3000)  # Warte 3 Sekunden, bevor ins Hauptmenü gewechselt wird
    main_menu()

click = False

def main_menu():
    global click
    while True:
        CurrentFramerate = int(clock.get_fps())
        pg.display.set_caption(f"Running at {CurrentFramerate} fps in {DefaultScreen_Width}x{DefaultScreen_Height}")
        mx, my = pg.mouse.get_pos()
        screen.fill((0, 0, 0))
        Background.draw_bg()
        Background.draw_ground()
        button_1 = pg.Rect(DefaultScreen_Width/2 - 50, DefaultScreen_Height/2 - 50, 100, 50)
        button_2 = pg.Rect(DefaultScreen_Width/2 - 50, DefaultScreen_Height/2 + 50, 100, 50)
        
        if button_1.collidepoint((mx, my)):
            if click:
                game()
        if button_2.collidepoint((mx, my)):
            if click:
                pg.quit()
                sys.exit()
                
        pg.draw.rect(screen, (150, 150, 150), button_1)
        pg.draw.rect(screen, (180, 180, 180), button_2)
                
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
    global enemy_gold
    running = True
    # Definiere Animationen (Pfad, Frame-Anzahl)
    player_animations_archer = {
        'idle':   ('assets/gfx/troops/type1/Idle.png', 4),
        'attack': ('assets/gfx/troops/type1/Attack.png', 6),
        'hurt':   ('assets/gfx/troops/type1/Hurt.png', 4),
        'archery':('assets/gfx/troops/type1/Archery.png', 6),
        'death':  ('assets/gfx/troops/type1/Death.png', 8),
        'walk':   ('assets/gfx/troops/type1/Walk.png', 6)
    }
    enemy_animations_archer = {
        'idle':   ('assets/gfx/troops/type1/Idle.png', 4),
        'attack': ('assets/gfx/troops/type1/Attack.png', 6),
        'hurt':   ('assets/gfx/troops/type1/Hurt.png', 4),
        'archery':('assets/gfx/troops/type1/Archery.png', 6),
        'death':  ('assets/gfx/troops/type1/Death.png', 8),
        'walk':   ('assets/gfx/troops/type1/Walk.png', 6)
    }
    player_animations_swordmen = {
        'idle':   ('assets/gfx/troops/type2/Idle.png', 4),
        'attack': ('assets/gfx/troops/type2/Attack2.png', 6),
        'hurt':   ('assets/gfx/troops/type2/Hurt.png', 4),
        'death':  ('assets/gfx/troops/type2/Death.png', 8),
        'walk':   ('assets/gfx/troops/type2/Walk.png', 6)
    }
    enemy_animations_swordmen = {
        'idle':   ('assets/gfx/troops/type2/Idle.png', 4),
        'attack': ('assets/gfx/troops/type2/Attack2.png', 6),
        'hurt':   ('assets/gfx/troops/type2/Hurt.png', 4),
        'death':  ('assets/gfx/troops/type2/Death.png', 8),
        'walk':   ('assets/gfx/troops/type2/Walk.png', 6)
    }

    
    troops_group = pg.sprite.LayeredUpdates()
    player_castle = Castle(castle_img_100, DefaultScreen_Width - 250, DefaultScreen_Height - 200, 0.2, team="player")
    enemy_castle = Castle(pg.transform.flip(castle_img_100,1,0), 0, DefaultScreen_Height - 200, 0.2, team="enemy")
    
    spawn_x = DefaultScreen_Width - 250
    spawn_y = DefaultScreen_Height - 50
    
    # Variablen für automatisches Spawnen vom Gegner
    enemy_spawn_timer = 0
    enemy_spawn_interval = 5000  # 5 Sekunden
    enemy_spawn_x = 300
    enemy_spawn_y = DefaultScreen_Height - 50
    enemy_unit_cost = 15  # Kosten pro feindlicher Einheit

    # Zusätzlich Buildtime/Cooldown für Spieler-Spawns (in Millisekunden)
    player_archer_build_timer = 0
    player_archer_cooldown = 2000  # z.B. 2 Sekunden
    player_swordfighter_build_timer = 0
    player_swordfighter_cooldown = 3000  # z.B. 3 Sekunden
    
    while running:
        dt = clock.tick(FPS)
        # Update der Build-Timer (sofern sie aktiv sind)
        if player_archer_build_timer > 0:
            player_archer_build_timer -= dt
        if player_swordfighter_build_timer > 0:
            player_swordfighter_build_timer -= dt
        enemy_spawn_timer += dt
        
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                # Spieler spawnt neuen Archer nur, wenn der Cooldown abgelaufen ist
                elif event.key == pg.K_1:
                    if player_archer_build_timer <= 0:
                        new_archer = ArcherTroop(player_animations_archer, spawn_x, spawn_y, scale=1, team="player")
                        troops_group.add(new_archer, layer=1)
                        player_archer_build_timer = player_archer_cooldown
                # Spieler spawnt neuen Swordfighter, wenn der entsprechende Cooldown abgelaufen ist
                elif event.key == pg.K_2:
                    if player_swordfighter_build_timer <= 0:
                        new_swordfighter = Troop(player_animations_swordmen, spawn_x, spawn_y, scale=1, team="player")
                        troops_group.add(new_swordfighter, layer=1)
                        player_swordfighter_build_timer = player_swordfighter_cooldown
                        
        # Automatischer Gegner-Spawn (wie bisher), wobei der Gegner seine Einheiten nur spawnt, wenn genügend Gold vorhanden ist.
        if enemy_spawn_timer >= enemy_spawn_interval:
            enemy_spawn_timer = 0
            if enemy_gold >= enemy_unit_cost:
                enemy_gold -= enemy_unit_cost
                number = random.randint(0, 1)
                if number == 1:
                    new_enemy = Troop(enemy_animations_archer, enemy_spawn_x, enemy_spawn_y, scale=1, team="enemy")
                    troops_group.add(new_enemy, layer=1)
                else:
                    new_enemy = Troop(enemy_animations_swordmen,enemy_spawn_x, enemy_spawn_y, scale=1, team="enemy")
                    troops_group.add(new_enemy, layer=1)
        
        handle_combat(troops_group, dt, player_castle, enemy_castle)
        troops_group.update(dt)#wert dt
        player_castle.update()
        enemy_castle.update()
        
        result = check_victory_condition(player_castle, enemy_castle)
        if result == "player_wins":
            show_end_screen("Du hast gewonnen!")
            return
        elif result == "enemy_wins":
            show_end_screen("Du hast verloren!")
            return

        screen.fill((0, 0, 0))
        Background.draw_bg()
        Background.draw_ground()
        
        player_castle.draw()
        draw_health_bar(screen, player_castle.rect, player_castle.health, player_castle.max_health)
        enemy_castle.draw()
        draw_health_bar(screen, enemy_castle.rect, enemy_castle.health, enemy_castle.max_health)
        
        # Zeige beide Konten an
        draw_text("Gold: " + str(player_gold), font, (255, 215, 0), screen, DefaultScreen_Width - 180, 20)
        draw_text("Enemy Gold: " + str(enemy_gold), font, (255, 215, 0),screen, 20, 20)
        
        troops_group.draw(screen)
        for troop in troops_group:
            draw_health_bar(screen, troop.rect, troop.health, troop.max_health)
            
        pg.display.update()

if __name__ == '__main__':
    main_menu()
