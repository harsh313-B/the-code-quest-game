import pygame
import random
import numpy as np

# Game window dimensions
WIDTH = 800
HEIGHT = 600

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill((100, 100, 100))  # Gray color for platforms
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            # Load and scale the flag image
            self.image = pygame.image.load("assets/flag.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 30))
        except Exception as e:
            print(f"Error loading flag image: {e}")
            # Fallback to a colored rectangle if image not found
            self.image = pygame.Surface((30, 30))
            self.image.fill((255, 215, 0))  # Gold color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Level:
    def __init__(self, maze_width=25, maze_height=25, topic="python_basics"):
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.topic = topic
        # Calculate wall and path sizes
        self.wall_size = min(WIDTH // maze_width, HEIGHT // maze_height)
        self.path_size = self.wall_size  # Path size equals wall size
        self.player_size = int(self.path_size * 0.8)  # Player is 80% of path size

    def create_level(self):
        maze_gen = MazeGenerator(self.maze_width, self.maze_height)
        self.maze, (start_x, start_y), (end_x, end_y) = maze_gen.generate()
        
        # Create wall sprites
        walls = pygame.sprite.Group()
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                if self.maze[y, x] == 1:
                    wall = Wall(x * self.wall_size, y * self.wall_size, 
                              self.wall_size, self.wall_size)
                    walls.add(wall)
        
        # Create player with size based on path gaps
        from player import Player
        player = Player(start_x * self.wall_size + (self.wall_size - self.player_size) // 2,
                       start_y * self.wall_size + (self.wall_size - self.player_size) // 2,
                       self.player_size, self.player_size)
        goal = Goal(end_x * self.wall_size, end_y * self.wall_size)
        
        return walls, goal, player

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))  # Gray walls
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = np.ones((height, width), dtype=int)

    def generate(self):
        self.maze.fill(1)
        start_x = 1
        start_y = self.height - 2
        end_x = self.width - 2
        end_y = 1
        
        # Generate the main maze
        self._generate_path(start_x, start_y)
        
        # Create a clear area around the flag
        # Make the flag position and surrounding area all paths (0)
        for y in range(max(0, end_y - 1), min(self.height, end_y + 2)):
            for x in range(max(0, end_x - 1), min(self.width, end_x + 2)):
                self.maze[y, x] = 0
        
        # Ensure start point is clear
        self.maze[start_y, start_x] = 0
            
        return self.maze, (start_x, start_y), (end_x, end_y)

    def _generate_path(self, x, y):
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (0 < new_x < self.width - 1 and 
                0 < new_y < self.height - 1 and 
                self.maze[new_y, new_x] == 1):
                self.maze[new_y, new_x] = 0
                self.maze[y + dy//2, x + dx//2] = 0
                self._generate_path(new_x, new_y)
