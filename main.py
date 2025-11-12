import pygame
import sys
import datetime
from pygame.locals import *
from code_editor import CodeEditor
from game_preview import GamePreview, Button

# Инициализация pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
CODE_EDITOR_WIDTH = 600
PREVIEW_WIDTH = 600
FPS = 60

# Цвета
BACKGROUND = (30, 30, 40)
TEXT_COLOR = (220, 220, 220)

class PythonGameEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Advanced Python Game Editor 3.14.0")
        self.clock = pygame.time.Clock()
        
        # Компоненты редактора
        self.code_editor = CodeEditor(0, 50, CODE_EDITOR_WIDTH, SCREEN_HEIGHT - 100)
        self.game_preview = GamePreview(CODE_EDITOR_WIDTH, 50, PREVIEW_WIDTH, SCREEN_HEIGHT - 100)
        
        # Кнопки
        self.run_button = Button(50, SCREEN_HEIGHT - 40, 100, 30, "Run Game", self.run_code)
        self.clear_button = Button(160, SCREEN_HEIGHT - 40, 100, 30, "Clear", self.clear_code)
        self.save_button = Button(270, SCREEN_HEIGHT - 40, 100, 30, "Save", self.save_code)
        self.load_button = Button(380, SCREEN_HEIGHT - 40, 100, 30, "Load", self.load_code)
        
        # Меню
        self.menu_buttons = [
            Button(10, 10, 80, 30, "File"),
            Button(100, 10, 100, 30, "Settings"),
            Button(210, 10, 80, 30, "Account"),
            Button(300, 10, 80, 30, "Profile")
        ]
        
        # Стартовый код для игры
        self.load_default_template()
        
        # Состояние приложения
        self.running = True
    
    def load_default_template(self):
        template = '''import pygame
import sys
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Game")

# Colors
BACKGROUND = (20, 30, 40)
PLAYER_COLOR = (86, 156, 214)
ENEMY_COLOR = (220, 100, 100)
BULLET_COLOR = (255, 215, 0)

# Player
player = pygame.Rect(WIDTH//2 - 15, HEIGHT - 50, 30, 30)
player_speed = 5

# Enemies
enemies = []
enemy_spawn_timer = 0

# Bullets
bullets = []
bullet_speed = 7

# Game state
score = 0
game_over = False
clock = pygame.time.Clock()

def spawn_enemy():
    x = random.randint(20, WIDTH - 20)
    enemy = pygame.Rect(x, -20, 25, 25)
    enemies.append(enemy)

def draw_text(text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Main game loop
while not game_over:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Shoot bullet
                bullet = pygame.Rect(player.centerx - 3, player.top, 6, 15)
                bullets.append(bullet)
    
    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] and player.right < WIDTH:
        player.x += player_speed
    
    # Spawn enemies
    enemy_spawn_timer += 1
    if enemy_spawn_timer >= 60:  # Spawn every 60 frames
        spawn_enemy()
        enemy_spawn_timer = 0
    
    # Update bullets
    for bullet in bullets[:]:
        bullet.y -= bullet_speed
        if bullet.bottom < 0:
            bullets.remove(bullet)
    
    # Update enemies
    for enemy in enemies[:]:
        enemy.y += 2
        if enemy.top > HEIGHT:
            enemies.remove(enemy)
            score += 1
        
        # Collision with player
        if enemy.colliderect(player):
            game_over = True
        
        # Collision with bullets
        for bullet in bullets[:]:
            if enemy.colliderect(bullet):
                if enemy in enemies:
                    enemies.remove(enemy)
                if bullet in bullets:
                    bullets.remove(bullet)
                score += 5
    
    # Draw everything
    screen.fill(BACKGROUND)
    
    # Draw player
    pygame.draw.rect(screen, PLAYER_COLOR, player)
    pygame.draw.rect(screen, (255, 255, 255), player, 2)
    
    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_COLOR, enemy)
        pygame.draw.rect(screen, (255, 255, 255), enemy, 2)
    
    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, BULLET_COLOR, bullet)
    
    # Draw score
    draw_text(f"Score: {score}", 36, WIDTH//2, 20)
    
    # Draw controls help
    draw_text("Use ARROWS to move, SPACE to shoot", 24, WIDTH//2, HEIGHT - 20, (200, 200, 200))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
'''
        self.code_editor.lines = template.split('\n')
    
    def run_code(self):
        code = self.code_editor.get_code()
        self.game_preview.execute_code(code)
        return True
    
    def clear_code(self):
        self.code_editor.lines = [""]
        self.code_editor.cursor_pos = [0, 0]
        return True
    
    def save_code(self):
        try:
            filename = f"game_code_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            with open(filename, 'w') as f:
                f.write(self.code_editor.get_code())
            print(f"Code saved as {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")
        return True
    
    def load_code(self):
        try:
            # В реальном приложении здесь был бы диалог выбора файла
            # Для демонстрации просто загружаем шаблон
            self.load_default_template()
            print("Loaded default template")
        except Exception as e:
            print(f"Error loading file: {e}")
        return True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            
            self.code_editor.handle_event(event)
            self.run_button.handle_event(event)
            self.clear_button.handle_event(event)
            self.save_button.handle_event(event)
            self.load_button.handle_event(event)
            
            for button in self.menu_buttons:
                button.handle_event(event)
    
    def draw(self):
        self.screen.fill(BACKGROUND)
        
        # Рисуем компоненты
        self.code_editor.draw(self.screen)
        self.game_preview.draw(self.screen)
        
        # Рисуем кнопки
        self.run_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        self.save_button.draw(self.screen)
        self.load_button.draw(self.screen)
        
        # Рисуем меню
        for button in self.menu_buttons:
            button.draw(self.screen)
        
        # Заголовок
        title_font = pygame.font.SysFont("arial", 24, bold=True)
        title = title_font.render("Advanced Python 3.14.0 Game Editor", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 15))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.code_editor.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    editor = PythonGameEditor()
    editor.run()
