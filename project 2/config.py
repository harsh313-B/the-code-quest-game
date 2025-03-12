import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
FONT = pygame.font.Font(None, 36)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eco Quest")

def draw_text(text, x, y, color=BLACK):
    text_surface = FONT.render(text, True, color)
    screen.blit(text_surface, (x, y))

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text("Eco Quest - Save the Earth!", 250, 100, GREEN)
        draw_text("Press ENTER to Start", 290, 300, BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    level_1()
        
        pygame.display.flip()

def level_1():
    challenge_text = "Write a function to clean the river (Type 'filter_water()')"
    user_input = ""
    correct_answer = "filter_water()"
    
    while True:
        screen.fill(WHITE)
        draw_text("Level 1: Clean the Polluted River", 220, 100, GREEN)
        draw_text(challenge_text, 100, 200, BLACK)
        draw_text(user_input, 100, 300, BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_input == correct_answer:
                        draw_text("Correct! River is clean!", 250, 400, GREEN)
                        pygame.display.flip()
                        pygame.time.delay(2000)
                        main_menu()
                    else:
                        draw_text("Incorrect! Try again.", 250, 400, (200, 0, 0))
                        user_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode
        
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
