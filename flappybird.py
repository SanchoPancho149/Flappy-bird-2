import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
PIPE_WIDTH = 52
PIPE_HEIGHT = 400
GAP_SIZE = 150  # Gap between pipes

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Setup screen and mixer
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')
pygame.mixer.init()

# Load and scale images from 'images' folder
bird_image_original = pygame.image.load('images/bird.png').convert_alpha()
bird_image_original = pygame.transform.scale(bird_image_original, (BIRD_WIDTH, BIRD_HEIGHT))

pipe_image_original = pygame.image.load('images/pipe.png').convert_alpha()
pipe_image_top = pygame.transform.scale(pipe_image_original, (PIPE_WIDTH, PIPE_HEIGHT))
pipe_image_bottom = pygame.transform.flip(pipe_image_top, False, True)  # Flip vertically for bottom pipe

background_original = pygame.image.load('images/background.jpg').convert()
background = pygame.transform.scale(background_original, (SCREEN_WIDTH, SCREEN_HEIGHT))

cloud_image_original = pygame.image.load('images/cloud.png').convert_alpha()
cloud_image = pygame.transform.scale(cloud_image_original, (100, 50))

# Load sounds from 'sounds' folder
jump_sound = pygame.mixer.Sound('sounds/jump.mp3')
win_sound = pygame.mixer.Sound('sounds/win.mp3')
lose_sound = pygame.mixer.Sound('sounds/lose.mp3')

# Fonts
font = pygame.font.Font(None, 36)
class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(0, PIPE_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT // 2 - 50)

    def move(self):
        self.x -= 5

    def draw(self):
        screen.blit(cloud_image, (self.x, self.y))
# Bird class
class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 4
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0

    def flap(self):
        self.velocity = -10
        jump_sound.play()

    def move(self):
        self.velocity += 1  # Gravity effect
        self.y += self.velocity

    def draw(self):
        angle = min(max(-self.velocity * 3, -30), 30)
        rotated_bird_image = pygame.transform.rotate(bird_image_original, angle)
        new_rect = rotated_bird_image.get_rect(center=(self.x + BIRD_WIDTH // 2, self.y + BIRD_HEIGHT // 2))
        screen.blit(rotated_bird_image, new_rect.topleft)

# Pipe class
class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.height_top = random.randint(50, SCREEN_HEIGHT - GAP_SIZE - 50)
        self.height_bottom = SCREEN_HEIGHT - GAP_SIZE - self.height_top

    def move(self):
        self.x -= 5

    def draw(self):
        screen.blit(pipe_image_top, (self.x, -PIPE_HEIGHT + self.height_top))
        screen.blit(pipe_image_bottom, (self.x, SCREEN_HEIGHT - self.height_bottom))

def show_game_over():
    # Capture the current screen
    frozen_screen = screen.copy()
    
    while True:
        # Display the frozen screen
        screen.blit(frozen_screen, (0, 0))
        
        # Display "YOU LOST" message and restart button
        lost_text = font.render("YOU LOST", True, RED)
        restart_text = font.render("Restart?", True, BLACK)
        
        screen.blit(lost_text, (SCREEN_WIDTH // 2 - lost_text.get_width() // 2,
                                SCREEN_HEIGHT // 2 - lost_text.get_height() // 2 - 40))
        
        restart_button_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                            SCREEN_HEIGHT // 2 + restart_text.get_height()))
        
        screen.blit(restart_text, restart_button_rect.topleft)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    main() # Restart the game
        
        pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    bird = Bird()
    pipes = [Pipe()]
    clouds = [Cloud()]
    score = 0
    
    # Background position for scrolling effect
    bg_x1 = 0
    bg_x2 = background.get_width()

    # Display start message
    start_message_displayed=False
    
    while True:
        if not start_message_displayed:
            screen.fill(WHITE)
            start_text=font.render("Press SPACE to start", True, BLACK)
            screen.blit(start_text,
                        (SCREEN_WIDTH//2-start_text.get_width()//2,
                         SCREEN_HEIGHT//2-start_text.get_height()//2))
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_SPACE:
                        start_message_displayed=True
        
        else:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_SPACE:
                        bird.flap()

            # Move bird and pipes
            bird.move()

            for pipe in pipes:
                pipe.move()

                # Check if bird has passed a pipe to increase score and play sound once per pipe pass 
                if pipe.x + PIPE_WIDTH < bird.x <= pipe.x + PIPE_WIDTH + abs(5): 
                    score +=1 
                    win_sound.play()

                if pipe.x<-PIPE_WIDTH: 
                    pipes.remove(pipe) 
                    pipes.append(Pipe())
                    clouds.append(Cloud())

                # Collision detection with pipes or ground/ceiling 
                if (bird.y<pipe.height_top or bird.y+BIRD_HEIGHT>SCREEN_HEIGHT-pipe.height_bottom) and \
                   (pipe.x<bird.x+BIRD_WIDTH<pipe.x+PIPE_WIDTH): 
                    lose_sound.play() # Play lose sound on collision 
                    show_game_over()   # Show game over screen

                if bird.y>SCREEN_HEIGHT or bird.y<0: 
                    lose_sound.play() # Play lose sound on hitting ground/ceiling 
                    show_game_over()   # Show game over screen

            for cloud in clouds:
                cloud.move()
                cloud.draw()
                
                if cloud.x < -100:  # Remove clouds that move off-screen
                    clouds.remove(cloud)

            # Move background for scrolling effect 
            bg_x1-=1 
            bg_x2-=1
            
            if bg_x1<=-background.get_width(): 
                bg_x1=background.get_width()
            
            if bg_x2<=-background.get_width(): 
                bg_x2=background.get_width()

            # Draw everything on the screen including the moving background 
            screen.blit(background,(bg_x1 ,0)) 
            screen.blit(background,(bg_x2 ,0))

            for pipe in pipes: 
                pipe.draw()

            bird.draw()

            # Display score 
            score_text=font.render(f"Score: {score}", True ,BLACK) 
            screen.blit(score_text,(10 ,10))

            # Refresh display and set frame rate 
            pygame.display.flip() 
            clock.tick(30)

if __name__=='__main__':
    main()