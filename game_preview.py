import pygame
import sys
import os
import subprocess
import tempfile

class GamePreview:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height))
        self.last_output = None
        self.error_message = None
        self.execution_time = 0
        self.font = pygame.font.SysFont("arial", 14)
    
    def draw(self, screen):
        # Фон превью
        pygame.draw.rect(screen, (25, 25, 35), self.rect)
        
        # Заголовок
        title_font = pygame.font.SysFont("arial", 18, bold=True)
        title = title_font.render("Game Preview", True, (220, 220, 220))
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.top + 10))
        
        # Время выполнения
        time_text = self.font.render(f"Execution time: {self.execution_time:.3f}s", True, (220, 220, 220))
        screen.blit(time_text, (self.rect.left + 10, self.rect.top + 40))
        
        # Ошибки или вывод
        if self.error_message:
            error_text = self.font.render("Error:", True, (255, 100, 100))
            screen.blit(error_text, (self.rect.left + 10, self.rect.top + 70))
            
            y_offset = 100
            for line in self.error_message.split('\n'):
                if y_offset < self.rect.height - 30:
                    error_line = self.font.render(line, True, (255, 100, 100))
                    screen.blit(error_line, (self.rect.left + 20, self.rect.top + y_offset))
                    y_offset += 20
        elif self.last_output:
            output_text = self.font.render("Output:", True, (100, 255, 150))
            screen.blit(output_text, (self.rect.left + 10, self.rect.top + 70))
            
            y_offset = 100
            for line in self.last_output.split('\n'):
                if y_offset < self.rect.height - 30:
                    output_line = self.font.render(line, True, (100, 255, 150))
                    screen.blit(output_line, (self.rect.left + 20, self.rect.top + y_offset))
                    y_offset += 20
        else:
            help_text = self.font.render("Write your game code and click 'Run' to see preview", True, (220, 220, 220))
            screen.blit(help_text, (self.rect.centerx - help_text.get_width() // 2, self.rect.centery))
    
    def execute_code(self, code):
        start_time = pygame.time.get_ticks()
        
        try:
            # Создаем временный файл для выполнения кода
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Выполняем код и перехватываем вывод
            result = subprocess.run([sys.executable, temp_file], 
                                  capture_output=True, text=True, timeout=5)
            
            self.last_output = result.stdout
            self.error_message = result.stderr if result.stderr else None
            
            # Удаляем временный файл
            os.unlink(temp_file)
            
        except subprocess.TimeoutExpired:
            self.error_message = "Execution timed out (5 seconds)"
            self.last_output = None
        except Exception as e:
            self.error_message = f"Execution error: {str(e)}"
            self.last_output = None
        
        self.execution_time = (pygame.time.get_ticks() - start_time) / 1000.0

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.font = pygame.font.SysFont("arial", 16)
    
    def draw(self, screen):
        color = (100, 160, 210) if self.hovered else (70, 130, 180)
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (220, 220, 220), self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, (220, 220, 220))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                return self.action()
        return False
