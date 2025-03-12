import pygame
from level import Level, Platform, Goal

# Add these constants at the top of the file
WIDTH = 800
HEIGHT = 600

class PlatformLevel:
    def __init__(self, platforms, goal_position, topic="python_basics"):
        self.platforms = platforms
        self.goal_position = goal_position
        self.topic = topic
        self.player_width = 30
        self.player_height = 40

    def create_level(self):
        from player import Player
        platforms = pygame.sprite.Group()
        for platform in self.platforms:
            platforms.add(Platform(*platform))
        goal = Goal(*self.goal_position)
        player = Player(x=100, y=HEIGHT - 200, width=self.player_width, height=self.player_height)
        return platforms, goal, player

# Define both platform and maze levels
levels = [
    # Platform-based levels (first 3 levels)
    PlatformLevel(  # Level 1: Simple right-moving steps
        platforms=[
            (0, HEIGHT - 20, WIDTH, 20),  # Floor
            (100, 450, 150, 20),  # First step
            (350, 380, 150, 20),  # Second step
            (600, 310, 150, 20),  # Third step
        ],
        goal_position=(650, 260),
        topic="python_basics"
    ),
    PlatformLevel(  # Level 2: Balanced steps
        platforms=[
            (0, HEIGHT - 20, WIDTH, 20),  # Floor
            (100, 450, 180, 20),   # Left platform
            (400, 380, 180, 20),  # Middle platform
            (700, 310, 100, 20),  # Right platform
        ],
        goal_position=(720, 260),
        topic="data_structures"
    ),
    PlatformLevel(  # Level 3: Symmetrical platforms
        platforms=[
            (0, HEIGHT - 20, WIDTH, 20),  # Floor
            (WIDTH//2 - 200, 450, 400, 20),  # Wide bottom
            (WIDTH//2 - 150, 350, 300, 20),  # Medium middle
            (WIDTH//2 - 75, 250, 150, 20),   # Small top
        ],
        goal_position=(WIDTH//2, 200),
        topic="basic_syntax"
    ),
    # Maze-based levels (next 3 levels)
    Level(maze_width=15, maze_height=15, topic="loops"),
    Level(maze_width=20, maze_height=20, topic="functions"),
    Level(maze_width=25, maze_height=25, topic="algorithms")
]
