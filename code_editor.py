import pygame
from pygame.locals import *

class CodeEditor:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.lines = [""]
        self.cursor_pos = [0, 0]  # [line, column]
        self.scroll_offset = 0
        self.font = pygame.font.SysFont("consolas", 16)
        self.line_height = 20
        self.visible_lines = height // self.line_height
        self.selection_start = None
        self.cursor_blink = True
        self.blink_timer = 0
        
        # Python keywords for syntax highlighting
        self.keywords = {
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'import',
            'from', 'as', 'return', 'try', 'except', 'finally', 'with',
            'global', 'nonlocal', 'lambda', 'pass', 'break', 'continue',
            'and', 'or', 'not', 'is', 'in', 'None', 'True', 'False'
        }
        
        self.types = {'int', 'float', 'str', 'bool', 'list', 'dict', 'tuple'}
        
    def draw(self, screen):
        # Фон редактора
        pygame.draw.rect(screen, (25, 25, 35), self.rect)
        
        # Номера строк
        line_number_rect = pygame.Rect(self.rect.left, self.rect.top, 40, self.rect.height)
        pygame.draw.rect(screen, (40, 40, 50), line_number_rect)
        
        # Видимые строки
        start_line = self.scroll_offset
        end_line = min(start_line + self.visible_lines, len(self.lines))
        
        for i in range(start_line, end_line):
            y_pos = self.rect.top + (i - start_line) * self.line_height
            
            # Номер строки
            line_num_text = self.font.render(str(i + 1), True, (128, 128, 128))
            screen.blit(line_num_text, (self.rect.left + 5, y_pos))
            
            # Текст строки с подсветкой синтаксиса
            text_x = self.rect.left + 45
            self.draw_syntax_highlighted_line(screen, self.lines[i], text_x, y_pos)
        
        # Курсор
        if self.cursor_blink:
            cursor_x = self.rect.left + 45 + self.font.size(self.lines[self.cursor_pos[0]][:self.cursor_pos[1]])[0]
            cursor_y = self.rect.top + (self.cursor_pos[0] - self.scroll_offset) * self.line_height
            pygame.draw.line(screen, (255, 255, 255), (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + self.line_height), 2)
    
    def draw_syntax_highlighted_line(self, screen, line, x, y):
        tokens = self.tokenize_line(line)
        current_x = x
        
        for token_type, token_text in tokens:
            if token_type == 'keyword':
                color = (86, 156, 214)  # Синий
            elif token_type == 'string':
                color = (206, 145, 120)  # Оранжевый
            elif token_type == 'comment':
                color = (87, 166, 74)   # Зеленый
            elif token_type == 'number':
                color = (181, 206, 168) # Светло-зеленый
            elif token_type == 'type':
                color = (78, 201, 176)  # Бирюзовый
            else:
                color = (220, 220, 220)
            
            token_surface = self.font.render(token_text, True, color)
            screen.blit(token_surface, (current_x, y))
            current_x += self.font.size(token_text)[0]
    
    def tokenize_line(self, line):
        tokens = []
        i = 0
        n = len(line)
        
        while i < n:
            # Комментарии
            if line[i] == '#':
                tokens.append(('comment', line[i:]))
                break
            
            # Строки
            elif line[i] in ('"', "'"):
                quote = line[i]
                j = i + 1
                while j < n and line[j] != quote:
                    j += 1
                if j < n:
                    j += 1
                tokens.append(('string', line[i:j]))
                i = j
                continue
            
            # Числа
            elif line[i].isdigit():
                j = i
                while j < n and (line[j].isdigit() or line[j] == '.'):
                    j += 1
                tokens.append(('number', line[i:j]))
                i = j
                continue
            
            # Идентификаторы и ключевые слова
            elif line[i].isalpha() or line[i] == '_':
                j = i
                while j < n and (line[j].isalnum() or line[j] == '_'):
                    j += 1
                word = line[i:j]
                if word in self.keywords:
                    tokens.append(('keyword', word))
                elif word in self.types:
                    tokens.append(('type', word))
                else:
                    tokens.append(('normal', word))
                i = j
                continue
            
            # Прочие символы
            else:
                tokens.append(('normal', line[i]))
                i += 1
        
        return tokens
    
    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                self.insert_newline()
            elif event.key == K_BACKSPACE:
                self.backspace()
            elif event.key == K_DELETE:
                self.delete()
            elif event.key == K_TAB:
                self.insert_text("    ")
            elif event.key == K_UP:
                self.move_cursor_up()
            elif event.key == K_DOWN:
                self.move_cursor_down()
            elif event.key == K_LEFT:
                self.move_cursor_left()
            elif event.key == K_RIGHT:
                self.move_cursor_right()
            elif event.key == K_HOME:
                self.cursor_pos[1] = 0
            elif event.key == K_END:
                self.cursor_pos[1] = len(self.lines[self.cursor_pos[0]])
            elif event.key == K_PAGEUP:
                self.scroll_offset = max(0, self.scroll_offset - self.visible_lines)
                self.cursor_pos[0] = max(0, self.cursor_pos[0] - self.visible_lines)
            elif event.key == K_PAGEDOWN:
                self.scroll_offset = min(len(self.lines) - self.visible_lines, 
                                       self.scroll_offset + self.visible_lines)
                self.cursor_pos[0] = min(len(self.lines) - 1, 
                                       self.cursor_pos[0] + self.visible_lines)
            else:
                if event.unicode:
                    self.insert_text(event.unicode)
            
            self.cursor_blink = True
            self.blink_timer = 0
            
        elif event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.handle_click(event.pos)
    
    def insert_text(self, text):
        line = self.lines[self.cursor_pos[0]]
        self.lines[self.cursor_pos[0]] = line[:self.cursor_pos[1]] + text + line[self.cursor_pos[1]:]
        self.cursor_pos[1] += len(text)
        self.adjust_scroll()
    
    def insert_newline(self):
        current_line = self.lines[self.cursor_pos[0]]
        indent = len(current_line) - len(current_line.lstrip())
        
        self.lines[self.cursor_pos[0]] = current_line[:self.cursor_pos[1]]
        self.lines.insert(self.cursor_pos[0] + 1, " " * indent + current_line[self.cursor_pos[1]:])
        
        self.cursor_pos[0] += 1
        self.cursor_pos[1] = indent
        self.adjust_scroll()
    
    def backspace(self):
        if self.cursor_pos[1] > 0:
            line = self.lines[self.cursor_pos[0]]
            self.lines[self.cursor_pos[0]] = line[:self.cursor_pos[1]-1] + line[self.cursor_pos[1]:]
            self.cursor_pos[1] -= 1
        elif self.cursor_pos[0] > 0:
            current_line = self.lines.pop(self.cursor_pos[0])
            self.cursor_pos[0] -= 1
            self.cursor_pos[1] = len(self.lines[self.cursor_pos[0]])
            self.lines[self.cursor_pos[0]] += current_line
        self.adjust_scroll()
    
    def delete(self):
        line = self.lines[self.cursor_pos[0]]
        if self.cursor_pos[1] < len(line):
            self.lines[self.cursor_pos[0]] = line[:self.cursor_pos[1]] + line[self.cursor_pos[1]+1:]
        elif self.cursor_pos[0] < len(self.lines) - 1:
            next_line = self.lines.pop(self.cursor_pos[0] + 1)
            self.lines[self.cursor_pos[0]] += next_line
        self.adjust_scroll()
    
    def move_cursor_up(self):
        if self.cursor_pos[0] > 0:
            self.cursor_pos[0] -= 1
            self.cursor_pos[1] = min(self.cursor_pos[1], len(self.lines[self.cursor_pos[0]]))
            self.adjust_scroll()
    
    def move_cursor_down(self):
        if self.cursor_pos[0] < len(self.lines) - 1:
            self.cursor_pos[0] += 1
            self.cursor_pos[1] = min(self.cursor_pos[1], len(self.lines[self.cursor_pos[0]]))
            self.adjust_scroll()
    
    def move_cursor_left(self):
        if self.cursor_pos[1] > 0:
            self.cursor_pos[1] -= 1
        elif self.cursor_pos[0] > 0:
            self.cursor_pos[0] -= 1
            self.cursor_pos[1] = len(self.lines[self.cursor_pos[0]])
        self.adjust_scroll()
    
    def move_cursor_right(self):
        line = self.lines[self.cursor_pos[0]]
        if self.cursor_pos[1] < len(line):
            self.cursor_pos[1] += 1
        elif self.cursor_pos[0] < len(self.lines) - 1:
            self.cursor_pos[0] += 1
            self.cursor_pos[1] = 0
        self.adjust_scroll()
    
    def handle_click(self, pos):
        rel_x = pos[0] - (self.rect.left + 45)
        rel_y = pos[1] - self.rect.top
        
        line_idx = self.scroll_offset + rel_y // self.line_height
        if 0 <= line_idx < len(self.lines):
            self.cursor_pos[0] = line_idx
            
            line = self.lines[line_idx]
            width = 0
            col = 0
            for i, char in enumerate(line):
                char_width = self.font.size(char)[0]
                if width + char_width / 2 > rel_x:
                    break
                width += char_width
                col = i + 1
            self.cursor_pos[1] = col
        
        self.cursor_blink = True
        self.blink_timer = 0
    
    def adjust_scroll(self):
        if self.cursor_pos[0] < self.scroll_offset:
            self.scroll_offset = self.cursor_pos[0]
        elif self.cursor_pos[0] >= self.scroll_offset + self.visible_lines:
            self.scroll_offset = self.cursor_pos[0] - self.visible_lines + 1
    
    def update(self, dt):
        self.blink_timer += dt
        if self.blink_timer >= 0.5:
            self.cursor_blink = not self.cursor_blink
            self.blink_timer = 0
    
    def get_code(self):
        return "\n".join(self.lines)
