import pygame
import sys
import random
import math
import os
from os import listdir
from os.path import isfile, join

pygame.init()
pygame.display.set_caption("FireWater")

# Constants
WIDTH, HEIGHT = 1344, 960
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))


def draw_menu(window, background, bg_image):
    font = pygame.font.Font(None, 36)

    button_width, button_height = 200, 50
    level1_button = pygame.Rect((WIDTH - button_width) // 2, HEIGHT // 2 - button_height, button_width, button_height)
    level2_button = pygame.Rect((WIDTH - button_width) // 2, HEIGHT // 2 + 30, button_width, button_height)

    # Draw the background
    for tile in background:
        window.blit(bg_image, tile)

    pygame.draw.rect(window, (78, 58, 58), level1_button)
    pygame.draw.rect(window, (78, 58, 58), level2_button)

    text_level1 = font.render("Level 1", True, (0, 0, 0))
    text_level2 = font.render("Level 2", True, (0, 0, 0))

    text_level1_pos = ((WIDTH - button_width) // 2 + button_width // 2 - text_level1.get_width() // 2,
                       HEIGHT // 2 - button_height + button_height // 2 - text_level1.get_height() // 2)
    text_level2_pos = ((WIDTH - button_width) // 2 + button_width // 2 - text_level2.get_width() // 2,
                       HEIGHT // 2 + 30 + button_height // 2 - text_level2.get_height() // 2)

    window.blit(text_level1, text_level1_pos)
    window.blit(text_level2, text_level2_pos)

    return level1_button, level2_button


def main_menu(window, background, bg_image):
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                level1_button, level2_button = draw_menu(window, background, bg_image)
                if level1_button.collidepoint(pygame.mouse.get_pos()):
                    return "maps/map1.txt"
                elif level2_button.collidepoint(pygame.mouse.get_pos()):
                    return "maps/map2.txt"

        level1_button, level2_button = draw_menu(window, background, bg_image)
        pygame.display.update()
        clock.tick(30)


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction = False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain3.png")
    image = pygame.image.load(path).convert_alpha()
    scaled_size = size // 2
    surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size) #localisation de l'image du terrain, ici le haut gfauche de l'image a charger c'est 96 en x et 0 en y. faut aussi changer le size
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface) #ici j'ai enlevé le .scale2x ca devrait faire apparaitre plus petit j'espère


class Player(pygame.sprite.Sprite):
    GRAVITY = 1 ##gravité
    SPRITES = None
    ANIMATION_DELAY = 3 ##pour faire aller plus ou moins vite les animations


    def __init__(self, x, y, width, height, fire):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0 ##gravité
        self.jump_count = 0 ##doublejump
        self.die = False
        self.finish = False
        if fire:
            self.SPRITES = load_sprite_sheets("MainCharacters", "fireboy", 32, 32, True)
        else:
            self.SPRITES = load_sprite_sheets("MainCharacters", "watergirl", 32, 32, True)
        self.width = width
        self.height = height

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1: ##doublejump
            self.count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def getX(self):
        return self.rect.x

    def make_die(self):
        self.die = True
    
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY) ##gravité
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1 ##gravité
        self.update_sprite()

    def landed(self):
        self.fall_count = 0 ##gravité
        self.y_vel = 0
        self. jump_count = 0 #doublejump

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.die:
            sprite_sheet = "die"
            sprites = self.SPRITES[sprite_sheet + "_" + self.direction]
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
            self.sprite = sprites[sprite_index]
            self.animation_count += 1
            if sprite_index == len(sprites) - 1:
                # Die animation is complete, remove the player
                self.die = False
                self.rect.x = -1000  # Move player off-screen
                self.rect.y = -1000  # Move player off-screen
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw (self, win):
        win.blit(self.sprite, (self.rect.x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))


class Endblock(Object):
    def __init__(self, x, y, width, height, name):
        super().__init__(x, y, width, height, name)
        self.endblock1 = load_sprite_sheets("Traps", "Endblock", width, height)
        self.image = self.endblock1[name][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = name


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, "block")
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Water(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "water")
        self.water = load_sprite_sheets("Traps", "Water", width, height)
        self.image = self.water["water"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "water"


class WaterAnimation(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "water4")
        self.water4 = load_sprite_sheets("Traps", "Water", width, height)
        self.image = self.water4["water4"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "water4"

    def loop(self):
        sprites = self.water4[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Lava(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "lava")
        self.lava = load_sprite_sheets("Traps", "Lava", width, height)
        self.image = self.lava["lava"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "lava"


class LavaAnimation(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "lava1")
        self.lava1 = load_sprite_sheets("Traps", "Lava", width, height)
        self.image = self.lava1["lava1"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "lava1"

    def loop(self):
        sprites = self.lava1[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = [i * width, j * height]
            tiles.append(pos)
    
    return tiles, image


def draw(window, background, bg_image, players, objects):
    for tile in background:
        window.blit(bg_image, tile)

    for player in players:
        player.draw(window)

    for obj in objects:
        obj.draw(window)

    
    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if isinstance(obj, WaterAnimation) or isinstance(obj, LavaAnimation):
            continue  # Skip collision check for animated water
        
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)
    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if not isinstance(obj, WaterAnimation) and not isinstance(obj, LavaAnimation) and pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
            
    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player1, player2, objects):
    keys = pygame.key.get_pressed()

    player1.x_vel = 0
    player2.x_vel = 0

    # Player 1 controls
    collide_left_p1 = collide(player1, objects, -PLAYER_VEL * 2)
    collide_right_p1 = collide(player1, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left_p1 and not player1.die:
        player1.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right_p1 and not player1.die:
        player1.move_right(PLAYER_VEL)

    vertical_collide_p1 = handle_vertical_collision(player1, objects, player1.y_vel)
    to_check_p1 = [collide_left_p1, collide_right_p1, *vertical_collide_p1]

    for obj in to_check_p1:
        if obj and obj.name == "water" and not player1.die:
            player1.make_die()

    # Player 2 controls
    collide_left_p2 = collide(player2, objects, -PLAYER_VEL * 2)
    collide_right_p2 = collide(player2, objects, PLAYER_VEL * 2)

    if keys[pygame.K_q] and not collide_left_p2 and not player2.die:
        player2.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right_p2 and not player2.die:
        player2.move_right(PLAYER_VEL)


    vertical_collide_p2 = handle_vertical_collision(player2, objects, player2.y_vel)
    to_check_p2 = [collide_left_p2, collide_right_p2, *vertical_collide_p2]
    
    for obj in to_check_p2:
        if obj and obj.name == "lava" and not player2.die:
            player2.make_die()
        
    if player1.getX() > WIDTH and player2.getX() > WIDTH:
        pygame.quit()
        quit()


def load_map(file_path, block_size):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    map_data = []
    for line in lines:
        row = [char for char in line.strip()]
        map_data.append(row)

    objects = []
    player1_start = None
    player2_start = None

    for y, row in enumerate(map_data):
        for x, char in enumerate(row):
            if char == 'w':
                objects.append(Block(x * block_size, y * block_size, block_size))
            elif char == 'e':
                objects.append(Water(x * block_size, y * block_size +  7 * 2, 24, 24))
                animation = WaterAnimation(x * block_size, y * block_size, 48, 48)
                objects.append(animation)
            elif char == 'l':
                objects.append(Lava(x * block_size, y * block_size + 7 * 2, 24, 24))
                animation = LavaAnimation(x * block_size, y * block_size, 48, 48)
                objects.append(animation)
            elif char == 'g':
                endblock1 = Endblock(x * block_size, y * block_size, 24, 24, "endblock1")
                objects.append(endblock1)
            elif char == 'f':
                endblock2 = Endblock(x * block_size, y * block_size, 24, 24, "endblock2")
                objects.append(endblock2)
            elif char == '1':
                player1_start = (x * block_size, y * block_size)
            elif char == '2':
                player2_start = (x * block_size, y * block_size)

    return objects, player1_start, player2_start

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Brick2.png")
    menu_background, menu_bg_image = get_background("Brick2.png")

    

    block_size = 48

    player1 = Player(0, 0, 50, 50, True)  # Initial position, will be adjusted by load_map
    player2 = Player(0, 0, 50, 50, False)  # Initial position, will be adjusted by load_map
    players = [player1, player2]

    # Load map from a text file
    map_file_path = main_menu(window, menu_background, menu_bg_image)
    map_objects, player1_start, player2_start = load_map(map_file_path, block_size)

    player1.rect.x, player1.rect.y = player1_start
    player2.rect.x, player2.rect.y = player2_start


    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player1.jump_count < 1 and not player1.die:
                    player1.jump()
                if event.key == pygame.K_z and player2.jump_count < 1 and not player2.die:
                    player2.jump()

        for p in players:
            p.loop(FPS)

        for obj in map_objects:
            if isinstance(obj, WaterAnimation) or isinstance(obj, LavaAnimation):
                obj.loop()

        handle_move(player1, player2, map_objects)
        draw(window, background, bg_image, [player1, player2], map_objects)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)