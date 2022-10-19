import pygame
from settings import *
from support import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)

        self.import_assets()
        self.objects = ('', '_idle', '_water', '_axe', '_hoe')
        self.active_object = ''
        self.active_cardinal = 'down'

        self.frame_index = 0

        # movement atributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(pos)
        self.speed = 200

        # Generate Sprite
        self.config_Sprite()

    def get_status(self):
        return self.active_cardinal + self.active_object

    def config_Sprite(self):
        self.status = self.get_status()
        # General Setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=self.pos)

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}

        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = - 1
            self.active_cardinal = 'up'
            self.active_object = ''

        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.active_cardinal = 'down'
            self.active_object = ''
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.active_cardinal = 'right'
            self.active_object = ''
        elif keys[pygame.K_LEFT]:
            self.direction.x = - 1
            self.active_cardinal = 'left'
            self.active_object = ''
        else:
            self.direction.x = 0

    def move(self, dt):
        # normalizing a vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
            self.frame_index = (self.frame_index + 1) % 4
        else:
            self.active_object = '_idle'
            self.frame_index = 0

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y

    def update(self, dt):
        self.input()
        self.move(dt)
        self.config_Sprite()
