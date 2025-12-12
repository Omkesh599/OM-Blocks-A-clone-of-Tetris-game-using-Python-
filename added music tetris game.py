import pygame
import random

# --- Configuration ---
CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS
FPS = 90
# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0)     # Z
]

# Tetromino shapes
SHAPES = {
    'I': ["0000","1111","0000","0000"],
    'J': ["100","111","000"],
    'L': ["001","111","000"],
    'O': ["11","11"],
    'S': ["011","110","000"],
    'T': ["010","111","000"],
    'Z': ["110","011","000"]
}

SHAPE_KEYS = list(SHAPES.keys())


def rotate(shape):
    w = len(shape[0])
    h = len(shape)
    new = []
    for x in range(w):
        row = ''.join(shape[h - 1 - y][x] if x < len(shape[y]) else '0' for y in range(h))
        new.append(row)
    return [r.rstrip() for r in new]


class Piece:
    def __init__(self, shape_key):
        self.shape_key = shape_key
        self.shape = [row for row in SHAPES[shape_key]]
        self.color = COLORS[SHAPE_KEYS.index(shape_key)]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = rotate(self.shape)

    @property
    def width(self):
        return len(self.shape[0])

    @property
    def height(self):
        return len(self.shape)


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.lines = 0

    def inside(self, x, y):
        return 0 <= x < COLS and 0 <= y < ROWS

    def valid(self, piece, offset_x=0, offset_y=0):
        for r, row in enumerate(piece.shape):
            for c, ch in enumerate(row):
                if ch == '1':
                    x = piece.x + c + offset_x
                    y = piece.y + r + offset_y
                    if not self.inside(x, y) or (y >= 0 and self.grid[y][x] is not None):
                        return False
        return True

    def lock_piece(self, piece):
        for r, row in enumerate(piece.shape):
            for c, ch in enumerate(row):
                if ch == '1':
                    x = piece.x + c
                    y = piece.y + r
                    if 0 <= y < ROWS and 0 <= x < COLS:
                        self.grid[y][x] = piece.color
        self.clear_lines()

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = ROWS - len(new_grid)
        if cleared > 0:
            for _ in range(cleared):
                new_grid.insert(0, [None] * COLS)
            self.grid = new_grid
            points = [0, 100, 300, 500, 800]
            self.score += points[cleared] * self.level
            self.lines += cleared
            self.level = 1 + self.lines // 10


def draw_grid(surface):
    for x in range(COLS + 1):
        pygame.draw.line(surface, GRAY, (x * CELL_SIZE, 0), (x * CELL_SIZE, HEIGHT))
    for y in range(ROWS + 1):
        pygame.draw.line(surface, GRAY, (0, y * CELL_SIZE), (WIDTH, y * CELL_SIZE))


def draw_board(surface, board):
    for y in range(ROWS):
        for x in range(COLS):
            cell = board.grid[y][x]
            if cell:
                pygame.draw.rect(surface, cell, (x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2))


def draw_piece(surface, piece, offset_x=0, offset_y=0):
    for r, row in enumerate(piece.shape):
        for c, ch in enumerate(row):
            if ch == '1':
                x = piece.x + c + offset_x
                y = piece.y + r + offset_y
                if y >= 0:
                    pygame.draw.rect(surface, piece.color,
                                     (x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2))


def new_piece():
    return Piece(random.choice(SHAPE_KEYS))


def game_over(board):
    return any(cell is not None for cell in board.grid[0])


def main():
    pygame.init()
    pygame.mixer.init()  # required for music

    # ------------------- MUSIC SECTION -------------------
    
    try:
        pygame.mixer.music.load("music-for-puzzle-game-146738 (1) - Copy.mp3")
        pygame.mixer.music.play(-1)  # loop forever
    except:
        print("Music file not found. Add correct path.")

    # -----------------------------------------------------

    screen = pygame.display.set_mode((WIDTH + 200, HEIGHT))
    pygame.display.set_caption("Om Blocks")
    clock = pygame.time.Clock()

    board = Board()
    current = new_piece()
    next_piece = new_piece()

    fall_time = 0
    fall_speed = 0.8
    paused = False

    font = pygame.font.SysFont("Arial", 20, bold=True)
    big_font = pygame.font.SysFont("Arial", 30, bold=True)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        if not paused:
            fall_time += dt

        speed = fall_speed / (1 + (board.level - 1) * 0.12)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT and board.valid(current, offset_x=-1):
                        current.x -= 1
                    elif event.key == pygame.K_RIGHT and board.valid(current, offset_x=1):
                        current.x += 1
                    elif event.key == pygame.K_DOWN and board.valid(current, offset_y=1):
                        current.y += 1
                        fall_time = 0
                    elif event.key == pygame.K_UP:
                        original_shape = current.shape[:]
                        current.rotate()
                        if not board.valid(current):
                            if board.valid(current, offset_x=-1):
                                current.x -= 1
                            elif board.valid(current, offset_x=1):
                                current.x += 1
                            elif board.valid(current, offset_y=-1):
                                current.y -= 1
                            else:
                                current.shape = original_shape
                    elif event.key == pygame.K_SPACE:
                        while board.valid(current, offset_y=1):
                            current.y += 1
                        board.lock_piece(current)
                        current = next_piece
                        next_piece = new_piece()
                        fall_time = 0

        if not paused:
            if fall_time > speed:
                fall_time = 0
                if board.valid(current, offset_y=1):
                    current.y += 1
                else:
                    board.lock_piece(current)
                    if game_over(board):
                        board = Board()
                    current = next_piece
                    next_piece = new_piece()

        screen.fill(BLACK)
        play_surface = pygame.Surface((WIDTH, HEIGHT))
        play_surface.fill(BLACK)

        draw_board(play_surface, board)
        draw_piece(play_surface, current)
        draw_grid(play_surface)
        screen.blit(play_surface, (0, 0))

        ui_x = WIDTH + 10
        pygame.draw.rect(screen, (30, 30, 30), (WIDTH, 0, 200, HEIGHT))
        title = big_font.render("Om Blocks", True, WHITE)
        screen.blit(title, (ui_x + 30, 10))

        nxt = font.render("Next:", True, WHITE)
        screen.blit(nxt, (ui_x + 10, 60))

        preview_surface = pygame.Surface((CELL_SIZE * 4, CELL_SIZE * 4))
        preview_surface.fill((20, 20, 20))
        temp_piece = Piece(next_piece.shape_key)
        temp_piece.x = 1
        temp_piece.y = 1
        draw_piece(preview_surface, temp_piece)
        screen.blit(preview_surface, (ui_x + 30, 90))

        screen.blit(font.render(f"Score: {board.score}", True, WHITE), (ui_x + 10, 220))
        screen.blit(font.render(f"Level: {board.level}", True, WHITE), (ui_x + 10, 240))
        screen.blit(font.render(f"Lines: {board.lines}", True, WHITE), (ui_x + 10, 260))

        screen.blit(font.render("Arrows: Move", True, WHITE), (ui_x + 10, 340))
        screen.blit(font.render("Up: Rotate", True, WHITE), (ui_x + 10, 360))
        screen.blit(font.render("Space: Hard drop", True, WHITE), (ui_x + 10, 380))
        screen.blit(font.render("P: Pause", True, WHITE), (ui_x + 10, 400))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
