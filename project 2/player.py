# FILE: player.py (Python)
import pygame
from level import Platform  # Add this import

# Add these constants at the top of the file
WIDTH = 800
HEIGHT = 600

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width=30, height=40):
        super().__init__()
        self.width = width
        self.height = height
        
        # Load player sprites
        try:
            self.sprites = []
            # Load running sprites
            for i in range(3):  # Assuming you have 3 running frames
                sprite = pygame.image.load(f"assets/character_malePerson_run{i}.png").convert_alpha()
                sprite = pygame.transform.scale(sprite, (width, height))
                self.sprites.append(sprite)
            
            # Load falling sprite
            self.fall_sprite = pygame.image.load("assets/character_maleAdventurer_fall.png").convert_alpha()
            self.fall_sprite = pygame.transform.scale(self.fall_sprite, (width, height))
        except:
            # Fallback to colored rectangle if images not found
            self.sprites = [pygame.Surface((width, height))]
            self.sprites[0].fill((0, 255, 0))
            self.fall_sprite = self.sprites[0]
        
        self.current_frame = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Movement variables
        self.speed = 5
        self.jump_power = -12
        self.gravity = 0.5
        self.direction = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing_right = True

    def update(self, keys, walls_or_platforms):
        if isinstance(walls_or_platforms, pygame.sprite.Group) and len(walls_or_platforms) > 0:
            first_sprite = next(iter(walls_or_platforms))
            if isinstance(first_sprite, Platform):
                self.update_platform_movement(keys, walls_or_platforms)
            else:
                self.update_maze_movement(keys, walls_or_platforms)

    def update_platform_movement(self, keys, platforms):
        # Horizontal movement
        self.direction.x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True

        # Apply horizontal movement
        self.rect.x += self.direction.x * self.speed

        # Platform collisions - horizontal
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.direction.x > 0:
                    self.rect.right = platform.rect.left
                if self.direction.x < 0:
                    self.rect.left = platform.rect.right

        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.direction.y = self.jump_power
            self.on_ground = False

        # Apply gravity
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

        # Platform collisions - vertical
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.direction.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.direction.y = 0
                    self.on_ground = True
                elif self.direction.y < 0:
                    self.rect.top = platform.rect.bottom
                    self.direction.y = 0

        # Animation
        if not self.on_ground:
            self.image = self.fall_sprite
        elif self.direction.x != 0:
            self.current_frame = (self.current_frame + 0.2) % len(self.sprites)
            self.image = self.sprites[int(self.current_frame)]
        else:
            self.image = self.sprites[0]

        # Flip sprite based on direction
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        # Window borders
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.direction.y = 0
            self.on_ground = True

    def update_maze_movement(self, keys, walls):
        old_x = self.rect.x
        old_y = self.rect.y
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_right = True
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            
        # Animation for maze movement
        if old_x != self.rect.x or old_y != self.rect.y:
            self.current_frame = (self.current_frame + 0.2) % len(self.sprites)
            self.image = self.sprites[int(self.current_frame)]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            
        # Wall collisions
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.rect.x = old_x
                self.rect.y = old_y
                break
