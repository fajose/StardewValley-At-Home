import pygame
from settings import *
from support import *
from timer import Timer


class Player(pygame.sprite.Sprite):
	def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil):
		super().__init__(group)

		# variable for status and sprites
		self.import_assets()
		self.active_obj = '_idle'
		self.active_card = 'down'

		# tools
		self.tools = ['hoe', 'axe', 'water']
		self.tool_index = 0
		self.active_tool = self.tools[self.tool_index]

		self.status = 'down_idle'
		self.frame_index = 0

		# seeds
		self.seeds = ['corn', 'tomato']
		self.seed_index = 0
		self.active_seed = self.seeds[self.seed_index]

		# Inventory
		self.inventory = {'wood': 0,
						  'apple': 0,
						  'corn': 0,
						  'tomato': 0}

		# interaction
		self.tree_sprites = tree_sprites
		self.interaction = interaction
		self.sleep = False
		self.soil = soil

		# general setup
		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(center=pos)

		self.z = LAYERS['main']

		# movement attributes
		self.direction = pygame.math.Vector2()
		self.pos = pygame.math.Vector2(self.rect.center)
		self.speed = 200

		# collisions
		self.collision_sprites = collision_sprites
		self.hitbox = self.rect.copy().inflate((-126, -70))

		# timers
		self.timers = {'tool_use': Timer(350, self.use_tool),
					   'tool_switch': Timer(200),
					   'seed_switch': Timer(200),
					   'seed_use': Timer(350, self.use_seed)
					   }

	def use_seed(self):
		self.soil.plant_seed(self.target_pos, self.active_seed)

	def use_tool(self):
		if self.active_tool == 'hoe':
			self.soil.get_hit(self.target_pos)

		if self.active_tool == 'water':
			self.soil.water(self.target_pos)

		if self.active_tool == 'axe':
			for tree in self.tree_sprites.sprites():
				if tree.rect.collidepoint(self.target_pos):
					tree.damage()

	def get_target_pos(self):
		self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.active_card]

	def import_assets(self):
		self.animations = {'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
						   'right_hoe':[],'left_hoe':[],'up_hoe':[],'down_hoe':[],
						   'right_axe':[],'left_axe':[],'up_axe':[],'down_axe':[],
						   'right_water':[],'left_water':[],'up_water':[],'down_water':[]}

		for animation in self.animations.keys():
			full_path = '../graphics/character/' + animation
			self.animations[animation] = import_folder(full_path)

	def animate(self, dt):
		self.get_status()
		self.frame_index += 4 * dt
		if self.frame_index >= len(self.animations[self.status]):
			self.frame_index = 0

		self.image = self.animations[self.status][int(self.frame_index)]

	def input(self):
		keys = pygame.key.get_pressed()

		if not self.timers['tool_use'].active and not self.timers['seed_use'].active and not self.sleep:
			if keys[pygame.K_UP]:
				self.direction.y = -1
				self.active_card = 'up'

			elif keys[pygame.K_DOWN]:
				self.direction.y = 1
				self.active_card = 'down'
			else:
				self.direction.y = 0

			if keys[pygame.K_RIGHT]:
				self.direction.x = 1
				self.active_card = 'right'

			elif keys[pygame.K_LEFT]:
				self.direction.x = -1
				self.active_card = 'left'
			else:
				self.direction.x = 0

			# tool use
			if keys[pygame.K_SPACE]:
				self.timers['tool_use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			if keys[pygame.K_LCTRL]:
				self.timers['seed_use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			if keys[pygame.K_q] and not self.timers['tool_switch'].active:
				self.timers['tool_switch'].activate()
				self.tool_index = (self.tool_index + 1) % len(self.tools)
				self.active_tool = self.tools[self.tool_index]

			if keys[pygame.K_w] and not self.timers['seed_switch'].active:
				self.timers['seed_switch'].activate()
				self.seed_index = (self.seed_index + 1) % len(self.seeds)
				self.active_seed = self.seeds[self.seed_index]

			if keys[pygame.K_RETURN]:
				collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
				if collided_interaction_sprite:
					if collided_interaction_sprite[0].name == 'Trader':
						pass
					else:
						self.active_card = 'left'
						self.active_obj = 'idle'
						self.direction = pygame.math.Vector2()
						self.frame_index = 0
						self.sleep = True

	def get_status(self):
		if self.timers['tool_use'].active:
			self.active_obj = '_' + self.active_tool
		elif self.direction.magnitude() == 0:
			self.active_obj = '_idle'
		else:
			self.active_obj = ''

		self.status = self.active_card + self.active_obj

	def update_timers(self):
		for timer in self.timers.values():
			timer.update()

	def collision(self, direction):
		for sprite in self.collision_sprites.sprites():
			if hasattr(sprite, 'hitbox'):
				if sprite.hitbox.colliderect(self.hitbox):
					if direction == 'horizontal':
						if self.direction.x > 0:
							self.hitbox.right = sprite.hitbox.left
						if self.direction.x < 0:
							self.hitbox.left = sprite.hitbox.right
					else:
						if self.direction.y > 0:
							self.hitbox.bottom = sprite.hitbox.top
						if self.direction.y < 0:
							self.hitbox.top = sprite.hitbox.bottom

	def move(self, dt):
		# normalizing a vector 
		if self.direction.magnitude() > 0:
			self.direction = self.direction.normalize()

		# horizontal movement
		self.pos.x += self.direction.x * self.speed * dt
		self.hitbox.centerx = round(self.pos.x)
		self.collision('horizontal')

		if self.hitbox.left < 0:
			self.hitbox.left = 0
		elif self.hitbox.right > WORLD_WIDTH:
			self.hitbox.right = WORLD_WIDTH

		self.rect.centerx = self.hitbox.centerx
		self.pos.x = self.hitbox.centerx

		# vertical movement
		self.pos.y += self.direction.y * self.speed * dt
		self.hitbox.centery = round(self.pos.y)
		self.collision('vertical')

		if self.hitbox.top < 0:
			self.hitbox.top = 0
		elif self.hitbox.bottom > WORLD_HEIGHT:
			self.hitbox.bottom = WORLD_HEIGHT

		self.rect.centery = self.hitbox.centery
		self.pos.y = self.hitbox.centery

	def update(self, dt):
		self.input()
		self.update_timers()
		self.move(dt)
		self.get_target_pos()
		self.animate(dt)
