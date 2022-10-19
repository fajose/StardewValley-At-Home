import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import choice

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil):

        # setup
        super().__init__(groups)
        self.plant_type = plant_type
        self.frames = import_folder(f'../graphics/fruit/{plant_type}/')
        self.soil = soil

        # growing
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False

        # sprite setup
        self.image = self.frames[self.age]
        self.y_offset = -16 if plant_type == 'corn' else -8
        self.y_offset = pygame.math.Vector2(0, self.y_offset)
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + self.y_offset)
        self.z = LAYERS['ground plant']

    def grow(self):
        self.age += self.grow_speed
        if self.age >= self.max_age:
            self.harvestable = True
            self.age = self.max_age

        self.image = self.frames[int(self.age)]
        self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + self.y_offset)

        if int(self.age) > 0:
            self.z = LAYERS['main']
            self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)


class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):

        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        self.collision_sprites = collision_sprites

        # graphics
        self.soil_watered = import_folder('../graphics/soil_water/')
        self.soil_surfs = import_floder_dict('../graphics/soil/')

        self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
         ground = pygame.image.load('../graphics/world/ground.png')
         h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE

         self.grid = [[{'Farmable': False, 'Soil': False, 'Water': None, 'Plant': None} for col in range(h_tiles)] for row in range(v_tiles)]
         for x,y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
             self.grid[y][x]['Farmable'] = True

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_cell, cell in enumerate(row):
                if cell['Farmable']:
                    x = TILE_SIZE * index_cell
                    y = TILE_SIZE * index_row
                    rect = pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if self.grid[y][x]['Farmable']:
                    self.grid[y][x]['Soil'] = True
                    self.create_soil_tiles()

                if self.grid[y][x]['Plant'] is not None:
                    self.grid[y][x]['Plant'].kill()
                    self.grid[y][x]['Plant'] = None

    def water(self, target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if self.grid[y][x]['Water'] is None:
                    surf = choice(self.soil_watered)
                    self.grid[y][x]['Water'] = WaterTile(soil_sprite.rect.topleft,
                                                         surf,
                                                         [self.all_sprites, self.water_sprites])

    def water_all(self):
        for soil_sprite in self.soil_sprites.sprites():
            x = soil_sprite.rect.x // TILE_SIZE
            y = soil_sprite.rect.y // TILE_SIZE
            if self.grid[y][x]['Water'] is None:
                surf = choice(self.soil_watered)
                self.grid[y][x]['Water'] = WaterTile(soil_sprite.rect.topleft,
                                                     surf,
                                                     [self.all_sprites, self.water_sprites])

    def remove_water(self):
        for sprite in self.water_sprites:
            sprite.kill()

        for row in self.grid:
            for cell in row:
                cell['Water'] = None

    def plant_seed(self, target_pos, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE

                if self.grid[y][x]['Plant'] is None:
                    self.grid[y][x]['Plant'] = Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite)

    def grow_plants(self):
        for plant in self.plant_sprites.sprites():
            x = plant.soil.rect.x // TILE_SIZE
            y = plant.soil.rect.y // TILE_SIZE

            if self.grid[y][x]['Water'] is not None:
                plant.grow()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_cell, cell in enumerate(row):
                if cell['Soil']:
                    tile_type = ''
                    if index_row < len(self.grid) - 1:
                        if self.grid[index_row + 1][index_cell]['Soil']:
                            tile_type += 't'

                    if index_row > 0:
                        if self.grid[index_row - 1][index_cell]['Soil']:
                            tile_type += 'b'

                    if index_cell > 0:
                        if row[index_cell - 1]['Soil']:
                            tile_type += 'r'

                    if index_cell < len(row) - 1:
                        if row[index_cell + 1]['Soil']:
                            tile_type += 'l'

                    if tile_type == '':
                        tile_type = 'o'
                    elif tile_type == 'tbrl':
                        tile_type = 'x'

                    SoilTile((index_cell * TILE_SIZE, index_row * TILE_SIZE),
                             self.soil_surfs[tile_type],
                             [self.all_sprites, self.soil_sprites])