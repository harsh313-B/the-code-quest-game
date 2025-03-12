import pygame
import sqlite3
from player import Player
from level import Platform, Goal
from database import Database  # Import Database
from levels import levels  # Import levels
import random
from typing import Optional, List
from question_generator import QuestionManager  # Add this import
import os
from random import randint, choice
import numpy as np

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create Game Window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Code Quest")

# Initialize Database
db = Database()
current_level = db.get_latest_level()  # Load last saved level

def quit_game():
    global running
    game_state.running = False
    return True

def start_game():
    global running, in_home_screen, player, goal, platforms, all_sprites, background, game_state
    try:
        player, goal, platforms, all_sprites, background = load_level(0)  # Start from level 1 (index 0)
        game_state.in_home_screen = False
        in_home_screen = False
        game_state.current_level = 1  # Reset to level 1
        game_state.score = 0  # Reset score
        game_state.reset_level_timer()
    except Exception as e:
        print(f"Error starting game: {e}")
        return

def load_level(level_index):
    level = levels[level_index]
    walls, goal, player = level.create_level()  # Get walls, goal and player from MazeLevel
    all_sprites = pygame.sprite.Group(player, goal, *walls)
    
    try:
        background = pygame.image.load("assets/background 1.png").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"Error loading background: {e}")
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((0, 0, 30))  # Dark blue background
    
    return player, goal, walls, all_sprites, background

# Initialize game objects as None
player = None
goal = None
platforms = None
all_sprites = None
background = pygame.Surface((WIDTH, HEIGHT))  # Create default background
background.fill(WHITE)  # Fill with white color

# Function to display score and time taken
def display_score_and_time(score, time_taken):
    # Dark blue background with gradient
    screen.fill((0, 0, 50))
    for i in range(HEIGHT):
        color = (0, 0, 50 + i * 50 // HEIGHT)
        pygame.draw.line(screen, color, (0, i), (WIDTH, i))

    font = pygame.font.Font(None, 74)
    title = font.render("Level Complete!", True, (0, 255, 100))
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title, title_rect)

    score_font = pygame.font.Font(None, 50)
    score_text = score_font.render(f"Score: {score}", True, (200, 200, 255))
    time_text = score_font.render(f"Time: {time_taken:.2f}s", True, (200, 200, 255))
    
    screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2))
    screen.blit(time_text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))

    # Add buttons
    next_button = Button("Next Level", WIDTH // 2 - 150, HEIGHT * 3 // 4, 140, 50, lambda: None)
    exit_button = Button("Exit", WIDTH // 2 + 10, HEIGHT * 3 // 4, 140, 50, lambda: None)
    
    next_button.draw(screen)
    exit_button.draw(screen)
    pygame.display.flip()

    # Wait for button click
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if next_button.rect.collidepoint(event.pos):
                    return "next"
                if exit_button.rect.collidepoint(event.pos):
                    return "exit"
        clock.tick(60)

def show_game_complete_screen(final_score):
    screen.fill((0, 0, 50))  # Dark blue background
    for i in range(HEIGHT):
        color = (0, 0, 50 + i * 50 // HEIGHT)
        pygame.draw.line(screen, color, (0, i), (WIDTH, i))

    font = pygame.font.Font(None, 74)
    title = font.render("Game Complete!", True, (0, 255, 100))  # Green text
    score = font.render(f"Final Score: {final_score}", True, (200, 200, 255))  # Light blue text
    
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    score_rect = score.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    screen.blit(title, title_rect)
    screen.blit(score, score_rect)

    # Create menu button
    menu_button = Button(
        "Back to Menu", 
        WIDTH // 2 - 100, 
        HEIGHT * 3 // 4, 
        200, 
        50,
        back_to_menu
    )

    # Wait for button click
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.rect.collidepoint(event.pos):
                    menu_button.callback()  # Call the back_to_menu function
                    return "menu"

        # Draw button every frame
        menu_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

# Button Class
class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 36)
        self.color = (100, 100, 100)
        self.hover_color = (150, 150, 150)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.color
        pygame.draw.rect(screen, color, self.rect)
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            if callable(self.callback):
                return self.callback()
            return self.callback
        return None

# TextBox Class
class TextBox:
    def __init__(self, x, y, width, height, text='', is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 255, 255)
        self.text = text
        self.display_text = '*' * len(text) if is_password else text
        self.font = pygame.font.Font(None, 36)
        self.txt_surface = self.font.render(self.display_text, True, BLACK)
        self.active = False
        self.is_password = is_password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.display_text = '*' * len(self.text) if self.is_password else self.text
                self.txt_surface = self.font.render(self.display_text, True, BLACK)

    def draw(self, screen):
        s = pygame.Surface((self.rect.width, self.rect.height))
        s.set_alpha(128)
        s.fill(WHITE)
        screen.blit(s, (self.rect.x, self.rect.y))
        
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        border_color = (100, 100, 255) if self.active else BLACK
        pygame.draw.rect(screen, border_color, self.rect, 2)

def sign_up_screen():
    username_box = TextBox(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
    password_box = TextBox(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    message = ""
    message_color = BLACK

    def handle_sign_up():
        nonlocal message, message_color
        success, msg = sign_up(username_box.text, password_box.text)
        message = msg
        message_color = (0, 255, 0) if success else (255, 0, 0)
        if success:
            pygame.time.delay(1000)
            return True
        return False

    sign_up_button = Button("Sign Up", WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50, handle_sign_up)
    back_button = Button("Back to Menu", WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50, back_to_menu)

    while True:
        screen.fill((0, 0, 30))  # Dark blue background for signup screen

        # Draw Title
        font = pygame.font.Font(None, 74)
        title_surf = font.render("Code Quest", True, (200, 200, 255))  # Light blue text
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surf, title_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            username_box.handle_event(event)
            password_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                result = sign_up_button.handle_click(event.pos)
                if result and result is True:
                    return
                result = back_button.handle_click(event.pos)
                if result:
                    return

        username_box.draw(screen)
        password_box.draw(screen)
        sign_up_button.draw(screen)
        back_button.draw(screen)

        if message:
            font = pygame.font.Font(None, 36)
            text = font.render(message, True, message_color)
            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 + 180))

        pygame.display.flip()

def login_screen():
    username_box = TextBox(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
    password_box = TextBox(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, is_password=True)
    message = ""
    message_color = BLACK

    def handle_login():
        nonlocal message, message_color
        success, msg = login(username_box.text, password_box.text)
        message = msg
        message_color = (0, 255, 0) if success else (255, 0, 0)
        if success:
            pygame.time.delay(1000)
            return True
        return False

    login_button = Button("Login", WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50, handle_login)
    back_button = Button("Back to Menu", WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50, back_to_menu)

    while True:
        screen.fill((0, 0, 30))  # Dark blue background for login screen

        # Draw Title
        font = pygame.font.Font(None, 74)
        title_surf = font.render("Code Quest", True, (200, 200, 255))  # Light blue text
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surf, title_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            username_box.handle_event(event)
            password_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                result = login_button.handle_click(event.pos)
                if result and result is True:
                    return
                result = back_button.handle_click(event.pos)
                if result:
                    return

        username_box.draw(screen)
        password_box.draw(screen)
        login_button.draw(screen)
        back_button.draw(screen)

        if message:
            font = pygame.font.Font(None, 36)
            text = font.render(message, True, message_color)
            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 + 180))

        pygame.display.flip()

def sign_up(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty"
    try:
        # Check if username already exists
        if db.check_username_exists(username):
            return False, "Username already exists"
        db.add_user(username, password)
        return True, "Successfully signed up!"
    except Exception as e:
        return False, f"Sign up failed: {str(e)}"

def login(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty"
    try:
        if db.check_user(username, password):
            global in_home_screen
            game_state.logged_in = True
            game_state.current_user = username
            in_home_screen = True  # Return to home screen instead of starting game
            return True, "Successfully logged in!"
        return False, "Invalid credentials"
    except Exception as e:
        return False, f"Login failed: {str(e)}"

# Home Screen
def home_screen():
    try:
        background = pygame.image.load("assets/background 0.png").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((0, 0, 30))  # Dark blue fallback

    # Create buttons with adjusted positions
    start_button = Button("Start Game", WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50, start_game)
    buttons = [start_button]

    if not game_state.logged_in:
        # Login and Sign up buttons for non-logged in users
        login_button = Button("Login", WIDTH // 2 - 100, HEIGHT // 2, 200, 50, login_screen)
        sign_up_button = Button("Sign Up", WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50, sign_up_screen)
        buttons.extend([login_button, sign_up_button])
    else:
        # History button for logged-in users, positioned below start button
        history_button = Button("History", WIDTH // 2 - 100, HEIGHT // 2, 200, 50, 
            lambda: show_history_screen(game_state.current_user))
        buttons.append(history_button)

    # Add quit button at the bottom
    quit_button = Button("Quit Game", WIDTH // 2 - 100, HEIGHT - 80, 200, 50, quit_game)
    buttons.append(quit_button)

    while in_home_screen and game_state.running:
        screen.fill(WHITE)
        screen.blit(background, (0, 0))

        font = pygame.font.Font(None, 74)
        title_surf = font.render("Code Quest", True, (200, 200, 255))
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surf, title_rect)

        if game_state.logged_in and game_state.current_user:
            player_font = pygame.font.Font(None, 48)
            player_text = f"Player: {game_state.current_user}"
            player_surf = player_font.render(player_text, True, (200, 200, 255))
            player_rect = player_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 50))
            screen.blit(player_surf, player_rect)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global running
                running = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    result = button.handle_click(event.pos)
                    if result and callable(result):
                        result()

def show_history_screen(username):
    history_screen = HistoryScreen(screen, db, username)
    result = history_screen.display()
    if result == "exit":
        game_state.running = False
    return True

# Main Game Loop
clock = pygame.time.Clock()
running = True
in_home_screen = True
score = 0
start_time = pygame.time.get_ticks()

class GameState:
    def __init__(self):
        self.running = True
        self.in_home_screen = True
        self.current_level = 1  # Start at level 1
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.logged_in = False
        self.current_user = None
        self.loading = False

    def reset_level_timer(self):
        self.start_time = pygame.time.get_ticks()

    def save_progress(self):
        if self.logged_in and self.current_user:
            db.save_progress(self.current_user, self.current_level, self.score)

class LoadingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.dots = 0
        self.last_update = pygame.time.get_ticks()

    def draw(self):
        self.screen.fill(WHITE)
        self.dots = (pygame.time.get_ticks() - self.last_update) // 500 % 4
        text = "Loading" + "." * self.dots
        text_surf = self.font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text_surf, text_rect)
        pygame.display.flip()

class QuestionDisplay:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.padding = 20
        self.line_height = 40
        self.width = WIDTH - 2 * self.padding
        
    def display_question(self, question):
        # Dark theme with blue gradient
        self.screen.fill((20, 20, 40))
        for i in range(HEIGHT):
            color = (20, 20, 40 + i * 40 // HEIGHT)
            pygame.draw.line(self.screen, color, (0, i), (WIDTH, i))

        y_position = self.padding * 2

        # Question title
        title_font = pygame.font.Font(None, 48)
        title_surf = title_font.render("Python Question", True, (255, 215, 0))  # Gold color
        title_rect = title_surf.get_rect(center=(WIDTH // 2, y_position))
        self.screen.blit(title_surf, title_rect)
        
        y_position += self.line_height * 2

        # Display question with white text
        lines = self._wrap_text(question.content, self.width)
        for line in lines:
            text_surf = self.font.render(line, True, (200, 200, 255))  # Light blue text
            self.screen.blit(text_surf, (self.padding, y_position))
            y_position += self.line_height

        y_position += self.line_height * 2
        option_rects = []

        # Create modern option buttons
        for i, option in enumerate(['A', 'B', 'C', 'D']):
            # Option box
            option_rect = pygame.Rect(
                WIDTH // 4,
                y_position + i * (self.line_height + 20),
                WIDTH // 2,
                self.line_height + 10
            )
            
            # Button gradient
            for y in range(option_rect.height):
                color = (60, 60, 140 + y * 40 // option_rect.height)
                pygame.draw.line(self.screen, color, 
                               (option_rect.left, option_rect.top + y),
                               (option_rect.right, option_rect.top + y))
            
            pygame.draw.rect(self.screen, (100, 100, 255), option_rect, 3)
            
            # Option letter
            letter_surf = self.font.render(f"{option}:", True, (255, 255, 255))
            self.screen.blit(letter_surf, (option_rect.left + 10, option_rect.top + 5))
            
            # Option text
            text_surf = self.font.render(question.options[i], True, (255, 255, 255))
            self.screen.blit(text_surf, (option_rect.left + 50, option_rect.top + 5))
            
            option_rects.append((option_rect, question.options[i]))

        pygame.display.flip()
        return self._handle_option_selection(option_rects)

    def display_result(self, correct: bool, explanation: str):
        self.screen.fill(WHITE)
        y_position = self.padding

        # Display result
        result_text = "Correct!" if correct else "Incorrect!"
        result_color = (0, 255, 0) if correct else (255, 0, 0)
        text_surf = self.font.render(result_text, True, result_color)
        self.screen.blit(text_surf, (self.padding, y_position))
        
        # Display explanation
        y_position += self.line_height * 2
        lines = self._wrap_text(explanation, self.width)
        for line in lines:
            text_surf = self.font.render(line, True, BLACK)
            self.screen.blit(text_surf, (self.padding, y_position))
            y_position += self.line_height

        pygame.display.flip()
        pygame.time.delay(3000)  # Show result for 3 seconds

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, BLACK)
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def _handle_option_selection(self, option_rects):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for rect, option in option_rects:
                        if rect.collidepoint(mouse_pos):
                            return option

class HistoryScreen:
    def __init__(self, screen, db, username):
        self.screen = screen
        self.db = db
        self.username = username
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.header_color = (200, 200, 255)
        self.row_colors = [(60, 60, 80), (40, 40, 60)]
        self.text_color = (255, 255, 255)
        
    def display(self):
        history = self.db.get_user_history(self.username)
        while True:
            self.screen.fill((30, 30, 50))
            title = self.title_font.render(f"Game History - {self.username}", True, (255, 215, 0))
            self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 40)))
            
            headers = ["Date", "Level", "Score", "Time (s)"]
            for i, header in enumerate(headers):
                text = self.font.render(header, True, self.header_color)
                self.screen.blit(text, text.get_rect(center=((WIDTH//4) * i + WIDTH//8, 100)))
            
            for i, entry in enumerate(history):
                y = 150 + i * 40
                if y > HEIGHT - 100: break
                pygame.draw.rect(self.screen, self.row_colors[i % 2], (0, y, WIDTH, 40))
                texts = [entry[0][:10], str(entry[1]), str(entry[2]), f"{entry[3]:.1f}"]
                for j, text in enumerate(texts):
                    surf = self.font.render(text, True, self.text_color)
                    self.screen.blit(surf, surf.get_rect(center=((WIDTH//4) * j + WIDTH//8, y + 20)))
            
            back_btn = Button("Back", WIDTH//2 - 50, HEIGHT - 80, 100, 40, back_to_menu)
            back_btn.draw(self.screen)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "exit"
                if event.type == pygame.MOUSEBUTTONDOWN and back_btn.rect.collidepoint(event.pos):
                    return "back"
            clock.tick(60)

def main_game_loop(game_state):
    global player, goal, platforms, all_sprites, background
    question_manager = QuestionManager()
    question_display = QuestionDisplay(screen)
    loading_screen = LoadingScreen(screen)
    clock = pygame.time.Clock()

    # Create reset button
    reset_button = Button("Reset", 10, 50, 100, 30, lambda: reset_level(game_state))

    def reset_level(game_state):
        global player, goal, platforms, all_sprites, background
        try:
            player, goal, platforms, all_sprites, background = load_level(game_state.current_level - 1)
            game_state.reset_level_timer()
        except Exception as e:
            print(f"Error resetting level: {e}")

    while game_state.running:
        if game_state.in_home_screen:
            home_screen()
            if not game_state.running:
                break
            # Reset player and level when returning to game
            player = None
            continue
        else:
            if not player:  # Initialize level if player doesn't exist
                try:
                    player, goal, platforms, all_sprites, background = load_level(game_state.current_level - 1)
                except Exception as e:
                    print(f"Error loading level: {e}")
                    game_state.running = False
                    break

            # Handle all events first
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    reset_button.handle_click(event.pos)

            clock.tick(FPS)
            screen.blit(background, (0, 0))

            # Handle player update
            keys = pygame.key.get_pressed()
            player.update(keys, platforms)

            # Update other sprites
            goal.update()
            for platform in platforms:
                platform.update()

            # Draw all sprites and UI
            all_sprites.draw(screen)
            reset_button.draw(screen)

            # Check for level completion
            if pygame.sprite.collide_rect(player, goal):
                # Get question for current level
                question = question_manager.get_question(
                    game_state.current_level,
                    levels[game_state.current_level - 1].topic
                )

                if question:
                    # Fade background
                    overlay = pygame.Surface((WIDTH, HEIGHT))
                    overlay.fill((0, 0, 0))
                    overlay.set_alpha(128)
                    screen.blit(overlay, (0, 0))
                    
                    # Display question and get answer
                    selected_answer = question_display.display_question(question)
                    if selected_answer:
                        correct = selected_answer == question.correct_answer
                        # Award points based on correctness
                        if correct:
                            game_state.score += 100
                            if game_state.logged_in:
                                time_taken = (pygame.time.get_ticks() - game_state.start_time) / 1000
                                db.add_history_entry(
                                    game_state.current_user,
                                    game_state.current_level,
                                    game_state.score,
                                    time_taken
                                )
                            # Display success message
                            question_display.display_result(True, question.explanation)
                        else:
                            # Display explanation for incorrect answer
                            question_display.display_result(False, question.explanation)

                        # Show level complete screen
                        end_time = pygame.time.get_ticks()
                        time_taken = (end_time - game_state.start_time) / 1000
                        result = display_score_and_time(game_state.score, time_taken)

                # Level completion logic
                if result == "exit":
                    game_state.in_home_screen = True
                    continue
                elif result == "next":
                    game_state.current_level += 1
                    if game_state.logged_in:
                        game_state.save_progress()

                    if game_state.current_level > len(levels):
                        result = show_game_complete_screen(game_state.score)
                        if result == "menu":
                            game_state.in_home_screen = True
                            game_state.current_level = 1  # Reset level
                            game_state.score = 0  # Reset score
                            player = None  # Reset player
                            continue
                        elif result == "exit":
                            game_state.running = False
                            break
                    else:
                        try:
                            player, goal, platforms, all_sprites, background = load_level(
                                game_state.current_level - 1)
                            game_state.reset_level_timer()
                        except Exception as e:
                            print(f"Error loading level: {e}")
                            game_state.running = False

            # Display current score
            score_text = pygame.font.Font(None, 36).render(
                f"Score: {game_state.score}", True, BLACK)
            screen.blit(score_text, (10, 10))

            pygame.display.flip()

# Update the back_to_menu function
def back_to_menu():
    global in_home_screen, player
    in_home_screen = True
    player = None  # Reset player when going back to menu
    return True

# Initialize game state and start the game
if __name__ == "__main__":
    game_state = GameState()
    main_game_loop(game_state)
    pygame.quit()

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = np.ones((height, width), dtype=int)  # 1 represents walls

    def generate(self):
        # Start with all walls
        self.maze.fill(1)
        
        # Create a path from start to end
        start_x = 1
        start_y = self.height - 2
        end_x = self.width - 2
        end_y = 1
        
        # Mark start and end
        self.maze[start_y, start_x] = 0
        self.maze[end_y, end_x] = 0
        
        # Generate maze using recursive backtracking
        self._generate_path(start_x, start_y)
        
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

# Update the Level class to use mazes
class Level:
    def __init__(self, maze_width=25, maze_height=25, topic="python_basics"):
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.topic = topic
        self.wall_size = min(WIDTH // maze_width, HEIGHT // maze_height)
        self.player_size = self.wall_size // 2

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
        
        # Create player and goal
        player = Player(start_x * self.wall_size, start_y * self.wall_size, 
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

