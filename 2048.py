import pygame
import numpy as np
import random


class Config:
    # Game constants
    BOARD_SIZE = 4
    TILE_SIZE = 150
    TILE_MARGIN = 10
    SCORE_MARGIN = 10
    SCORE_AREA_HEIGHT = 60
    FOUR_CHANCE = 0.08
    FPS = 60
    
    # Calculated sizes
    WINDOW_SIZE = BOARD_SIZE * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN
    
    # Colors
    BACKGROUND_COLOR = (30, 30, 30)
    TEXT_COLOR = (255, 255, 255)
    BLACK_TEXT = (0, 0, 0)
    EMPTY_TILE_COLOR = (119, 110, 101)
    UNKNOWN_TILE_COLOR = (60, 58, 50)
    
    TILE_COLORS = {
        2: (238, 228, 218),
        4: (237, 224, 200),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 204, 97),
        512: (237, 200, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46)
    }


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((
            Config.WINDOW_SIZE, 
            Config.WINDOW_SIZE + Config.SCORE_AREA_HEIGHT
        ))
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 60)
        
        self.board = Board()
        self.renderer = Renderer(self.screen, self.font)
        self.score = 0
        self.running = True
    
    def handle_input(self):
        """Handle keyboard input and return if the game should continue."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            elif event.type == pygame.KEYDOWN:
                moved = False
                score_increase = 0
                
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    moved, score_increase = self.board.move_up()
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    moved, score_increase = self.board.move_down()
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    moved, score_increase = self.board.move_left()
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    moved, score_increase = self.board.move_right()
                
                if moved:
                    self.score += score_increase
        
        return True
    
    def update(self):
        """Update game state."""
        if self.board.is_game_over():
            return False  # Game over
        return True  # Continue game
    
    def render(self):
        """Render the current game state."""
        if self.board.is_game_over():
            self.renderer.draw_game_over_screen(self.score)
        else:
            self.renderer.draw_board(self.board.get_board(), self.score)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            if not self.handle_input():
                break
            
            if not self.update():
                # Game over, but continue showing the screen until quit
                pass
            
            self.render()
            self.clock.tick(Config.FPS)
        
        pygame.quit()

class Board:
    def __init__(self):
        self.board = np.zeros((Config.BOARD_SIZE, Config.BOARD_SIZE))
        self._add_new_tile()
        self._add_new_tile()
    
    def get_board(self):
        return self.board.copy()
    
    def _compress_row(self, row):
        """Remove zeros and compress row to the left."""
        new_row = [num for num in row if num != 0]
        return new_row + [0] * (Config.BOARD_SIZE - len(new_row))
    
    def _add_new_tile(self):
        """Add a new tile (2 or 4) to a random empty position."""
        empty_positions = np.argwhere(self.board == 0)
        if len(empty_positions) == 0:
            return False
        
        try:
            row, col = random.choice(empty_positions)
            self.board[row][col] = 4 if random.random() < Config.FOUR_CHANCE else 2
            return True
        except (IndexError, ValueError):
            return False
    
    def _move_left_row(self, row):
        """Move and merge a single row to the left."""
        # Compress row
        new_row = self._compress_row(row)
        score = 0
        
        # Merge adjacent equal tiles
        for j in range(Config.BOARD_SIZE - 1):
            if new_row[j] != 0 and new_row[j] == new_row[j + 1]:
                new_row[j] *= 2
                score += new_row[j]
                new_row[j + 1] = 0
        
        # Compress again after merging
        new_row = self._compress_row(new_row)
        return new_row, score
    
    def move_left(self):
        """Move all tiles left and return (moved, score)."""
        old_board = self.board.copy()
        total_score = 0
        
        for i in range(Config.BOARD_SIZE):
            new_row, score = self._move_left_row(self.board[i])
            self.board[i] = new_row
            total_score += score
        
        moved = not np.array_equal(old_board, self.board)
        if moved:
            self._add_new_tile()
        
        return moved, total_score
    
    def move_right(self):
        """Move all tiles right."""
        self.board = np.rot90(self.board, 2)
        moved, score = self.move_left()
        self.board = np.rot90(self.board, 2)
        return moved, score
    
    def move_up(self):
        """Move all tiles up."""
        self.board = np.rot90(self.board)
        moved, score = self.move_left()
        self.board = np.rot90(self.board, 3)
        return moved, score
    
    def move_down(self):
        """Move all tiles down."""
        self.board = np.rot90(self.board, 3)
        moved, score = self.move_left()
        self.board = np.rot90(self.board)
        return moved, score
    
    def is_game_over(self):
        """Check if the game is over (no valid moves)."""
        # If there are empty tiles, game continues
        if np.any(self.board == 0):
            return False
        
        # Check if any move is possible by testing each direction
        test_board = Board()
        test_board.board = self.board.copy()
        
        for move_fn in [test_board.move_left, test_board.move_right, 
                       test_board.move_up, test_board.move_down]:
            moved, _ = move_fn()  # Returns 2 values
            if moved:
                return False
        
        return True

class Renderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
    
    def draw_board(self, board, score):
        """Draw the game board and score."""
        self.screen.fill(Config.BACKGROUND_COLOR)
        
        # Render score text
        score_text = self.font.render(f"Score: {int(score)}", True, Config.TEXT_COLOR)
        score_rect = score_text.get_rect(
            center=(self.screen.get_width() // 2, Config.TILE_MARGIN + score_text.get_height() // 2)
        )
        self.screen.blit(score_text, score_rect)
        
        # Offset the board below the score
        board_top_offset = score_rect.bottom + Config.SCORE_MARGIN
        
        # Draw tiles
        for r in range(Config.BOARD_SIZE):
            for c in range(Config.BOARD_SIZE):
                self._draw_tile(board[r][c], r, c, board_top_offset)
    
    def _draw_tile(self, value, row, col, board_top_offset):
        """Draw a single tile at the specified position."""
        rect = pygame.Rect(
            col * (Config.TILE_SIZE + Config.TILE_MARGIN) + Config.TILE_MARGIN,
            row * (Config.TILE_SIZE + Config.TILE_MARGIN) + Config.TILE_MARGIN + board_top_offset,
            Config.TILE_SIZE, Config.TILE_SIZE
        )
        
        # Choose tile color
        if value == 0:
            color = Config.EMPTY_TILE_COLOR
        else:
            color = Config.TILE_COLORS.get(value, Config.UNKNOWN_TILE_COLOR)
        
        # Draw tile background
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        
        # Draw tile text if not empty
        if value != 0:
            text = self.font.render(str(int(value)), True, Config.BLACK_TEXT)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
    
    def draw_game_over_screen(self, score):
        """Draw the game over screen."""
        self.screen.fill(Config.BACKGROUND_COLOR)
        text = self.font.render(f"Game Over! Score: {int(score)}", True, Config.TEXT_COLOR)
        text_rect = text.get_rect(
            center=(self.screen.get_width() // 2, Config.TILE_MARGIN + text.get_height() // 2)
        )
        self.screen.blit(text, text_rect)

def main():
    """Main entry point for the 2048 game."""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        pygame.quit()

if __name__ == '__main__':
    main()


