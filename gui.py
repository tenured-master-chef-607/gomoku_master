"""
Gomoku GUI Module
Author: TJ Qiu
Copyright © 2023 TJ Qiu. All rights reserved.
"""

import pygame
import sys
import os
import math
import random
from board import Board
from ai import GomokuAI

class GomokuGUI:
    def __init__(self, board_size=15, cell_size=40, margin=50):
        self.board_size = board_size
        self.cell_size = cell_size
        self.margin = margin
        self.window_size = (board_size * cell_size + 2 * margin, 
                          board_size * cell_size + 2 * margin + 50)  # Added space for buttons
        
        # Initialize Pygame
        pygame.init()
        
        # Set up the display
        os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center the window
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Gomoku - Five in a Row")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BROWN = (205, 170, 125)  # Lighter, warmer wood tone
        self.DARK_BROWN = (160, 120, 80)  # Darker wood tone for grid lines
        self.GRAY = (200, 200, 200)
        self.HOVER_COLOR = (255, 255, 255, 128)
        self.BUTTON_COLOR = (70, 130, 180)  # Steel blue
        self.BUTTON_HOVER_COLOR = (100, 160, 210)
        self.TEXT_COLOR = (50, 50, 50)  # Dark gray for text
        
        # Game state
        self.board = Board()
        self.difficulty = "medium"  # Default difficulty
        self.ai = GomokuAI(depth=3, difficulty=self.difficulty)
        self.game_over = False
        self.winner = None
        self.hover_pos = None
        self.player_color = None  # 1 for black, -1 for white
        self.showing_color_selection = True
        
        # Animation properties
        self.animation_stones = []  # [(row, col, color, alpha, size_factor)]
        self.fade_speed = 15
        self.grow_speed = 0.1
        
        # Button properties
        button_width = 120
        button_height = 36
        # Only have the restart button
        self.restart_button_rect = pygame.Rect(self.window_size[0] - self.margin - button_width, 
                                             self.window_size[1] - 45, button_width, button_height)
        self.restart_button_hover = False
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 28)
        self.message_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 20)
        
        # Load and create stone images with shadow effects
        self.stone_images = {}
        self._create_stone_images()
        
        # Create a wooden texture for the board background
        self._create_board_texture()
        
        # Create a simple icon
        icon_size = 32
        icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        icon.fill((0, 0, 0, 0))  # Transparent background
        pygame.draw.circle(icon, self.DARK_BROWN, (icon_size//2, icon_size//2), icon_size//2)  # Board
        pygame.draw.circle(icon, self.BLACK, (icon_size//2, icon_size//2), icon_size//3)  # Stone
        pygame.display.set_icon(icon)

    def _create_board_texture(self):
        """Create a wooden texture for the board."""
        self.board_texture = pygame.Surface(self.window_size)
        
        # Base color
        self.board_texture.fill(self.BROWN)
        
        # Add wood grain effect
        for _ in range(200):
            x = random.randint(0, self.window_size[0])
            y = random.randint(0, self.window_size[1])
            width = random.randint(2, 10)
            height = random.randint(10, 100)
            alpha = random.randint(5, 30)
            
            grain = pygame.Surface((width, height), pygame.SRCALPHA)
            color = (0, 0, 0, alpha) if random.random() < 0.5 else (255, 255, 255, alpha)
            grain.fill(color)
            self.board_texture.blit(grain, (x, y))

    def _create_stone_images(self):
        """Create stone images with shadow effects at different sizes."""
        for size_factor in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            stone_size = int((self.cell_size - 4) * size_factor)
            if stone_size <= 0:
                continue
                
            # Black stone with shadow
            black_stone = pygame.Surface((stone_size, stone_size), pygame.SRCALPHA)
            black_stone.fill((0, 0, 0, 0))  # Transparent
            
            # Shadow
            shadow_size = stone_size + 2
            shadow = pygame.Surface((shadow_size, shadow_size), pygame.SRCALPHA)
            pygame.draw.circle(shadow, (0, 0, 0, 128), (shadow_size//2, shadow_size//2), shadow_size//2)
            
            # Main stone with gradient
            center = stone_size // 2
            radius = stone_size // 2
            for x in range(stone_size):
                for y in range(stone_size):
                    distance = math.sqrt((x - center) ** 2 + (y - center) ** 2)
                    if distance <= radius:
                        # Create a lighting effect from top-left
                        brightness = 50 + max(0, min(150, (radius - distance) * 1.5))
                        if x < center and y < center:  # Upper left quadrant - highlight
                            brightness += 50
                        pygame.draw.circle(black_stone, (brightness, brightness, brightness), (x, y), 1)
            
            # Overlay to make it black
            overlay = pygame.Surface((stone_size, stone_size), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (0, 0, 0, 200), (center, center), radius)
            black_stone.blit(overlay, (0, 0))
            
            # White stone with shadow
            white_stone = pygame.Surface((stone_size, stone_size), pygame.SRCALPHA)
            white_stone.fill((0, 0, 0, 0))  # Transparent
            
            # Main stone with gradient
            for x in range(stone_size):
                for y in range(stone_size):
                    distance = math.sqrt((x - center) ** 2 + (y - center) ** 2)
                    if distance <= radius:
                        # Create a lighting effect from top-left
                        brightness = 200 + max(0, min(55, (radius - distance) * 0.8))
                        if x < center and y < center:  # Upper left quadrant - highlight
                            brightness = min(255, brightness + 30)
                        pygame.draw.circle(white_stone, (brightness, brightness, brightness), (x, y), 1)
            
            self.stone_images[(1, size_factor)] = (shadow, black_stone)
            self.stone_images[(-1, size_factor)] = (shadow, white_stone)

    def draw_color_selection(self):
        # Create gradient background
        for y in range(self.window_size[1]):
            alpha = 255 - int(y * 100 / self.window_size[1])
            pygame.draw.line(self.screen, (220, 180, 150, alpha), (0, y), (self.window_size[0], y))
        
        # Board texture overlay
        self.screen.blit(self.board_texture, (0, 0))
        
        # Draw decorative patterns
        for i in range(10):
            radius = 8 + i * 30
            pygame.draw.circle(self.screen, (0, 0, 0, 15), 
                             (self.window_size[0] // 2, self.window_size[1] // 2), radius, 1)
        
        # Draw title with shadow
        title = self.title_font.render("Choose Your Color", True, self.BLACK)
        title_shadow = self.title_font.render("Choose Your Color", True, (100, 100, 100))
        title_rect = title.get_rect(center=(self.window_size[0] // 2, self.window_size[1] // 4 - 30))
        self.screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title, title_rect)
        
        # Draw difficulty selection
        diff_title = self.button_font.render("Difficulty:", True, self.BLACK)
        diff_rect = diff_title.get_rect(center=(self.window_size[0] // 2, self.window_size[1] // 4 + 20))
        self.screen.blit(diff_title, diff_rect)
        
        # Difficulty buttons
        button_width = 80
        button_height = 30
        button_spacing = 10
        diff_options = ["Easy", "Medium", "Hard"]
        diff_colors = [(50, 180, 50), (50, 50, 180), (180, 50, 50)]
        diff_buttons = []
        
        # Calculate positions for 3 buttons centered
        total_width = button_width * 3 + button_spacing * 2
        start_x = (self.window_size[0] - total_width) // 2
        
        for i, (diff, color) in enumerate(zip(diff_options, diff_colors)):
            button_rect = pygame.Rect(start_x + i * (button_width + button_spacing), 
                                    diff_rect.bottom + 10, 
                                    button_width, button_height)
            diff_buttons.append((button_rect, diff.lower()))
            
            # Highlight currently selected difficulty
            alpha = 220 if self.difficulty == diff.lower() else 160
            pygame.draw.rect(self.screen, (*color, alpha), button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (0, 0, 0, 100), button_rect, 1, border_radius=5)
            
            # Button text
            diff_text = self.info_font.render(diff, True, self.WHITE)
            diff_text_rect = diff_text.get_rect(center=button_rect.center)
            self.screen.blit(diff_text, diff_text_rect)
        
        # Create selection buttons
        black_rect = pygame.Rect(self.window_size[0] // 4 - 70, self.window_size[1] // 2 - 20, 
                               140, 140)
        white_rect = pygame.Rect(3 * self.window_size[0] // 4 - 70, self.window_size[1] // 2 - 20,
                               140, 140)
        
        # Draw button backgrounds with hover effect
        mouse_pos = pygame.mouse.get_pos()
        black_hover = black_rect.collidepoint(mouse_pos)
        white_hover = white_rect.collidepoint(mouse_pos)
        
        # Draw black option (circle with glow effect)
        if black_hover:
            for i in range(3):
                glow_radius = 75 + i*3
                pygame.draw.circle(self.screen, (100, 100, 100, 100 - i*30), 
                                 black_rect.center, glow_radius)
        
        pygame.draw.circle(self.screen, (50, 50, 50), black_rect.center, 60)
        pygame.draw.circle(self.screen, self.BLACK, black_rect.center, 55)
        
        # Reflection on black stone
        pygame.draw.circle(self.screen, (100, 100, 100), 
                         (black_rect.centerx - 20, black_rect.centery - 20), 15)
        
        # Draw white option (circle with glow effect)
        if white_hover:
            for i in range(3):
                glow_radius = 75 + i*3
                pygame.draw.circle(self.screen, (100, 100, 100, 100 - i*30), 
                                 white_rect.center, glow_radius)
        
        pygame.draw.circle(self.screen, (50, 50, 50), white_rect.center, 60)
        pygame.draw.circle(self.screen, self.WHITE, white_rect.center, 55)
        
        # Reflection on white stone
        pygame.draw.circle(self.screen, (220, 220, 220), 
                         (white_rect.centerx - 20, white_rect.centery - 20), 15)
        
        # Label the options
        black_text = self.button_font.render("Black (First)", True, self.WHITE)
        black_text_rect = black_text.get_rect(center=(black_rect.centerx, black_rect.bottom + 30))
        self.screen.blit(black_text, black_text_rect)
        
        white_text = self.button_font.render("White (Second)", True, self.BLACK)
        white_text_rect = white_text.get_rect(center=(white_rect.centerx, white_rect.bottom + 30))
        self.screen.blit(white_text, white_text_rect)
        
        # Draw copyright text at the bottom of the screen
        copyright_text = self.info_font.render("© 2023 TJ Qiu. All rights reserved.", True, (70, 70, 70))
        copyright_rect = copyright_text.get_rect(midbottom=(self.window_size[0] // 2, self.window_size[1] - 10))
        self.screen.blit(copyright_text, copyright_rect)
        
        pygame.display.flip()
        
        return black_rect, white_rect, diff_buttons
        
    def handle_color_selection(self, pos, black_rect, white_rect, diff_buttons):
        # Check if difficulty buttons were clicked
        for button_rect, diff in diff_buttons:
            if button_rect.collidepoint(pos):
                self.difficulty = diff
                self.ai = GomokuAI(depth=3, difficulty=diff)
                return
        
        # Check if stone color buttons were clicked
        if black_rect.collidepoint(pos):
            self.player_color = 1  # Black
            self.showing_color_selection = False
            # Add starting animation
            self._add_starting_animation()
        elif white_rect.collidepoint(pos):
            self.player_color = -1  # White
            self.showing_color_selection = False
            # Add starting animation
            self._add_starting_animation()
            
            # Draw board to show initial state
            self.draw_board()
            
            # Make AI move first when player chooses white - show thinking status
            status_rect = pygame.Rect(self.window_size[0] // 2 - 100, 10, 200, 30)
            self._draw_status(status_rect, "AI thinking...", (200, 100, 50))
            pygame.display.flip()
            
            # Get AI's move
            ai_move = self.ai.get_best_move(self.board)
            if ai_move:
                self.board.make_move(*ai_move)
                self._add_stone_animation(*ai_move, 1)  # Add stone animation for AI's move
    
    def _add_starting_animation(self):
        """Add a board reveal animation."""
        # This could be implemented with more complex animations
        # For now, we'll just use a simple fade-in effect for the board
        pass
        
    def _add_stone_animation(self, row, col, color):
        """Add a new stone with animation effect."""
        self.animation_stones.append([row, col, color, 0, 0.1])  # [row, col, color, alpha, size]
    
    def _update_animations(self):
        """Update all ongoing animations."""
        updated_animations = []
        
        for stone in self.animation_stones:
            row, col, color, alpha, size = stone
            
            # Update alpha (fade-in)
            alpha = min(255, alpha + self.fade_speed)
            
            # Update size (grow effect)
            size = min(1.0, size + self.grow_speed)
            
            # Keep animation if not complete
            if alpha < 255 or size < 1.0:
                updated_animations.append([row, col, color, alpha, size])
                
        self.animation_stones = updated_animations
    
    def draw_board(self):
        # Draw background with texture
        self.screen.blit(self.board_texture, (0, 0))
        
        # Draw board frame
        board_width = self.board_size * self.cell_size
        board_rect = pygame.Rect(self.margin - 10, self.margin - 10, 
                              board_width + 20, board_width + 20)
        pygame.draw.rect(self.screen, self.DARK_BROWN, board_rect, 5, border_radius=3)
        
        # Add shadow to the board
        shadow = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 30))
        self.screen.blit(shadow, (board_rect.x + 5, board_rect.y + 5))
        
        # Draw grid lines - ensuring we draw from 0 to board_size-1 for both axes
        for i in range(self.board_size):
            # Horizontal lines
            pygame.draw.line(self.screen, self.DARK_BROWN,
                           (self.margin, self.margin + i * self.cell_size),
                           (self.margin + (self.board_size-1) * self.cell_size, self.margin + i * self.cell_size),
                           2)  # Thicker lines
            # Vertical lines
            pygame.draw.line(self.screen, self.DARK_BROWN,
                           (self.margin + i * self.cell_size, self.margin),
                           (self.margin + i * self.cell_size, self.margin + (self.board_size-1) * self.cell_size),
                           2)  # Thicker lines
        
        # Draw star points (traditional Go/Gomoku board markers)
        star_points = []
        if self.board_size >= 13:
            # For board size 13x13 or larger
            star_dist = 3 if self.board_size < 15 else 4
            center = self.board_size // 2
            star_points = [
                (center, center),  # Center
                (star_dist, star_dist),  # Top-left
                (star_dist, self.board_size - star_dist - 1),  # Bottom-left
                (self.board_size - star_dist - 1, star_dist),  # Top-right
                (self.board_size - star_dist - 1, self.board_size - star_dist - 1)  # Bottom-right
            ]
            
            # Add middle points for 19x19
            if self.board_size >= 19:
                star_points.extend([
                    (center, star_dist),  # Top-center
                    (center, self.board_size - star_dist - 1),  # Bottom-center
                    (star_dist, center),  # Left-center
                    (self.board_size - star_dist - 1, center)  # Right-center
                ])
                
        for point in star_points:
            row, col = point
            # Calculate exact center of the intersection
            center_x = self.margin + col * self.cell_size
            center_y = self.margin + row * self.cell_size
            pygame.draw.circle(self.screen, self.DARK_BROWN, (center_x, center_y), 4)
        
        # Draw hover effect
        if self.hover_pos and not self.game_over:
            row, col = self.hover_pos
            if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board.board[row][col] == 0:
                # Only show hover on empty cells
                # Calculate exact center of the intersection
                center_x = self.margin + col * self.cell_size
                center_y = self.margin + row * self.cell_size
                stone_color = 1 if self.board.current_player == 1 else -1
                
                # Get stone images
                shadow, stone = self.stone_images.get((stone_color, 1.0), (None, None))
                if shadow and stone:
                    # Draw semi-transparent shadow and stone
                    shadow.set_alpha(64)
                    stone.set_alpha(128)
                    shadow_size = shadow.get_width()
                    stone_size = stone.get_width()
                    self.screen.blit(shadow, (center_x - shadow_size//2 + 2, center_y - shadow_size//2 + 2))
                    self.screen.blit(stone, (center_x - stone_size//2, center_y - stone_size//2))
        
        # Draw stones with animations
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board.board[i][j] != 0:  # If there's a stone
                    # Calculate exact center of the intersection
                    center_x = self.margin + j * self.cell_size
                    center_y = self.margin + i * self.cell_size
                    
                    # Get stone images
                    shadow, stone = self.stone_images.get((self.board.board[i][j], 1.0), (None, None))
                    if shadow and stone:
                        # Ensure full opacity (0 transparency) for placed stones
                        shadow.set_alpha(255)
                        stone.set_alpha(255)
                        
                        shadow_size = shadow.get_width()
                        stone_size = stone.get_width()
                        self.screen.blit(shadow, (center_x - shadow_size//2 + 2, center_y - shadow_size//2 + 2))
                        self.screen.blit(stone, (center_x - stone_size//2, center_y - stone_size//2))
        
        # Draw animating stones
        for row, col, color, alpha, size in self.animation_stones:
            # Calculate exact center of the intersection
            center_x = self.margin + col * self.cell_size
            center_y = self.margin + row * self.cell_size
            
            # Get stone images for the current size
            shadow, stone = self.stone_images.get((color, size), (None, None))
            if shadow and stone:
                # Set alpha for fade-in effect
                shadow.set_alpha(alpha // 2)  # Shadow is more transparent
                stone.set_alpha(alpha)
                
                shadow_size = shadow.get_width()
                stone_size = stone.get_width()
                self.screen.blit(shadow, (center_x - shadow_size//2 + 2, center_y - shadow_size//2 + 2))
                self.screen.blit(stone, (center_x - stone_size//2, center_y - stone_size//2))
        
        # Draw restart button
        self._draw_button(self.restart_button_rect, "↺ Restart", self.restart_button_hover)
        
        # Draw controls info
        info_text = self.info_font.render("Left click: Place stone | Right click: Undo move", True, self.TEXT_COLOR)
        info_rect = info_text.get_rect(midtop=(self.window_size[0] // 2, self.window_size[1] - 45))
        self.screen.blit(info_text, info_rect)
        
        # Draw copyright text at the bottom of the screen
        copyright_text = self.info_font.render("© 2023 TJ Qiu. All rights reserved.", True, (70, 70, 70))
        copyright_rect = copyright_text.get_rect(midbottom=(self.window_size[0] // 2, self.window_size[1] - 5))
        self.screen.blit(copyright_text, copyright_rect)
        
        # Draw game status
        status_rect = pygame.Rect(self.window_size[0] // 2 - 100, 10, 200, 30)
        if self.game_over:
            if self.winner == self.player_color:
                status_text = "You won!"
            elif self.winner == -self.player_color:
                status_text = "AI won!"
            else:
                status_text = "Draw!"
            self._draw_status(status_rect, status_text, (50, 200, 50))
        else:
            if self.board.current_player == self.player_color:
                status_text = "Your turn"
                self._draw_status(status_rect, status_text, (50, 50, 200))
            else:
                # Only show "AI's turn" during AI's turn
                status_text = "AI's turn"
                self._draw_status(status_rect, status_text, (200, 50, 50))
        
        # Display difficulty level
        diff_colors = {"easy": (50, 180, 50), "medium": (50, 50, 180), "hard": (180, 50, 50)}
        diff_text = self.info_font.render(f"AI: {self.difficulty.capitalize()}", True, diff_colors[self.difficulty])
        diff_rect = diff_text.get_rect(topright=(self.window_size[0] - self.margin, 10))
        self.screen.blit(diff_text, diff_rect)
        
        pygame.display.flip()
    
    def _draw_button(self, rect, text, hover):
        # Draw button background with hover effect
        color = self.BUTTON_HOVER_COLOR if hover else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        
        # Add button shadow
        shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 40))
        shadow_rect = shadow.get_rect(topleft=(rect.x + 2, rect.y + 2))
        pygame.draw.rect(shadow, (0, 0, 0, 40), shadow.get_rect(), border_radius=5)
        self.screen.blit(shadow, shadow_rect)
        
        # Add button border
        pygame.draw.rect(self.screen, (40, 100, 150), rect, 1, border_radius=5)
        
        # Draw button text
        text_surf = self.button_font.render(text, True, self.WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def _draw_status(self, rect, text, color):
        # Draw status background
        pygame.draw.rect(self.screen, (*color, 180), rect, border_radius=15)
        pygame.draw.rect(self.screen, (*color, 220), rect, 1, border_radius=15)
        
        # Draw status text
        text_surf = self.button_font.render(text, True, self.WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def get_board_position(self, pos):
        x, y = pos
        # Convert pixel position to board coordinates
        # Use direct division instead of rounding to get exact cell
        col = int((x - self.margin + self.cell_size / 2) // self.cell_size)
        row = int((y - self.margin + self.cell_size / 2) // self.cell_size)
        
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return row, col
        return None
    
    def reset_game(self):
        self.board = Board()
        self.game_over = False
        self.winner = None
        self.hover_pos = None
        self.animation_stones = []  # Clear animations
        self.showing_color_selection = True  # Return to color selection screen
        # Preserve the chosen difficulty level
        self.ai = GomokuAI(depth=3, difficulty=self.difficulty)
    
    def undo_move(self):
        """Undo the last move and the AI's move before it."""
        if self.game_over:
            return
            
        # Only allow undo when it's the player's turn
        if self.board.current_player != self.player_color:
            return
            
        # Undo AI's move
        if self.board.undo_move():
            # Undo player's move
            self.board.undo_move()
            # Clear animations for undone moves
            self.animation_stones = []
    
    def run(self):
        clock = pygame.time.Clock()
        
        # Initialize color selection rects
        black_rect = None
        white_rect = None
        diff_buttons = []
        
        # For managing AI move timing
        ai_move_needed = False
        
        while True:
            clock.tick(60)  # Cap at 60 FPS for smooth animations
            
            # Check if AI needs to make a move
            if not self.showing_color_selection and not self.game_over and self.board.current_player != self.player_color and not ai_move_needed:
                # Set flag to make AI move on next frame (after drawing "AI's turn")
                ai_move_needed = True
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.showing_color_selection:
                    # Draw the color selection screen first to initialize the rects
                    black_rect, white_rect, diff_buttons = self.draw_color_selection()
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click only
                        self.handle_color_selection(event.pos, black_rect, white_rect, diff_buttons)
                    continue
                
                if event.type == pygame.MOUSEMOTION:
                    self.hover_pos = self.get_board_position(event.pos)
                    # Check if mouse is over buttons
                    self.restart_button_hover = self.restart_button_rect.collidepoint(event.pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check if restart button was clicked
                        if self.restart_button_rect.collidepoint(event.pos):
                            self.reset_game()
                            ai_move_needed = False
                        elif self.game_over:
                            self.reset_game()
                            ai_move_needed = False
                        else:
                            pos = self.get_board_position(event.pos)
                            if pos and 0 <= pos[0] < self.board_size and 0 <= pos[1] < self.board_size:
                                if self.board.make_move(*pos):
                                    # Add stone animation
                                    self._add_stone_animation(*pos, self.board.board[pos[0]][pos[1]])
                                    
                                    if self.board.check_win():
                                        self.game_over = True
                                        # The winner is the one who just placed the stone (player)
                                        self.winner = self.player_color
                    elif event.button == 3:  # Right click
                        if not self.game_over:
                            self.undo_move()  # Undo move on right click
            
            if not self.showing_color_selection:
                # Update animations
                self._update_animations()
                
                # Draw the board
                self.draw_board()
                
                # Handle AI move if needed (after board is drawn with "AI's turn" status)
                if ai_move_needed:
                    # Show thinking status
                    status_rect = pygame.Rect(self.window_size[0] // 2 - 100, 10, 200, 30)
                    self._draw_status(status_rect, "AI thinking...", (200, 100, 50))
                    pygame.display.flip()
                    
                    # Make AI move
                    ai_move = self.ai.get_best_move(self.board)
                    if ai_move:
                        self.board.make_move(*ai_move)
                        # Add stone animation for AI's move
                        self._add_stone_animation(*ai_move, self.board.board[ai_move[0]][ai_move[1]])
                        
                        if self.board.check_win():
                            self.game_over = True
                            # The winner is the AI
                            self.winner = -self.player_color
                    
                    # Reset flag
                    ai_move_needed = False

            # Small delay for performance
            pygame.time.delay(16)  # ~60 FPS

if __name__ == "__main__":
    game = GomokuGUI()
    game.run() 