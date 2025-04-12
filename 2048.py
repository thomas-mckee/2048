import pygame
import numpy as np
import random
import os 

BOARD_SIZE = 4
TILE_SIZE = 150
TILE_MARGIN = 10
SCORE_MARGIN = 10
WINDOW_SIZE = BOARD_SIZE * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN
FOUR_CHANCE = 0.08
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

# INITIALIZE GAME #
pygame.init()
score_area_height = 60
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + score_area_height))
pygame.display.set_caption("2048")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 60)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def init_board():
    board = np.zeros((BOARD_SIZE, BOARD_SIZE))
    add_new_tile(board)
    add_new_tile(board)
    return board


def add_new_tile(board):
    list = np.argwhere(board == 0)   
    row, col = random.choice(list)

    board[row][col] = 4 if random.random() < FOUR_CHANCE else 2
    
def move_left(board):
    moved = False
    scored = 0
    old_board = np.copy(board)
    for i in range(BOARD_SIZE): # for each row
        # compress by extracting all none-zero and append zeros to end of row
        new_row = [num for num in board[i] if num != 0]
        new_row = new_row + [0]*(BOARD_SIZE - len(new_row))
        board[i] = new_row
    
        # merge valid numbers
        for j in range(BOARD_SIZE - 1):
            if board[i][j] != 0 and board[i][j] == board[i][j+1]:
                board[i][j] = board[i][j] * 2
                scored += board[i][j]
                board[i][j+1] = 0

                new_row = [num for num in board[i] if num != 0]
                new_row = new_row + [0]*(BOARD_SIZE - len(new_row))
                board[i] = new_row

        # compress again
        new_row = [num for num in board[i] if num != 0]
        new_row = new_row + [0]*(BOARD_SIZE - len(new_row))
        board[i] = new_row
    
    if not np.array_equal(old_board, board):
        moved = True
    
    return board, moved, scored


def move_right(board):
    moved = False
    board = np.rot90(board, 2)
    board, moved, scored = move_left(board)
    board = np.rot90(board, 2)
    return board, moved, scored

def move_up(board):
    moved = False
    board = np.rot90(board)
    board, moved, scored = move_left(board)
    board = np.rot90(board, 3)
    return board, moved, scored

def move_down(board):
    moved = False
    board = np.rot90(board, 3)
    board, moved, scored = move_left(board)
    board = np.rot90(board)
    return board, moved, scored


def check_game_over(board):
    if np.any(board == 0):
        return False
    for move_fn in [move_left, move_right, move_up, move_down]:
        _, moved, __ = move_fn(board)
        if moved:
            return False
    return True

def draw_board(board, score):
    screen.fill((30, 30, 30))

    # Render score text
    score_text = font.render(f"Score: {int(score)}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(screen.get_width() // 2, TILE_MARGIN + score_text.get_height() // 2))
    screen.blit(score_text, score_rect)

    # Offset the board below the score
    board_top_offset = score_rect.bottom + SCORE_MARGIN

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            val = board[r][c]
            rect = pygame.Rect(
                c * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN,
                r * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN + board_top_offset,
                TILE_SIZE, TILE_SIZE
            )
            color = (119, 110, 101) if val == 0 else TILE_COLORS.get(val, (60, 58, 50))
            pygame.draw.rect(screen, color, rect, border_radius=8)
            if val != 0:
                text = font.render(str(int(val)), True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

def draw_quit_screen(score):
    screen.fill((30, 30, 30))
    text = font.render(f"Game Over! Score: {score}", True, (255, 255, 255))
    score_rect = text.get_rect(center=(screen.get_width() // 2, TILE_MARGIN + text.get_height() // 2))
    screen.blit(text, score_rect)

def main():
    # game setup
    board = init_board()
    running = True
    score = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                moved = False
                if event.key == pygame.K_w:
                    board, moved, scored = move_up(board)
                elif event.key == pygame.K_s:
                    board, moved, scored = move_down(board)
                elif event.key == pygame.K_a:
                    board, moved, scored = move_left(board)
                elif event.key == pygame.K_d:
                    board, moved, scored = move_right(board)
                if moved:
                    score += scored
                    add_new_tile(board)
        if check_game_over(board):
            draw_quit_screen(score)
        else: 
            draw_board(board, score)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()


