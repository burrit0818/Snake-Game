import pygame
import random
from pygame.math import Vector2

pygame.init()
pygame.mixer.init()

# ------------------ SETTINGS ------------------
TILE_SIZE = 40
GRID_SIZE = 15

PLAY_WIDTH = TILE_SIZE * GRID_SIZE
PLAY_HEIGHT = TILE_SIZE * GRID_SIZE

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

PLAY_X = (WINDOW_WIDTH - PLAY_WIDTH) // 2
PLAY_Y = (WINDOW_HEIGHT - PLAY_HEIGHT) // 2

FPS = 10

GREEN_BG = (175, 215, 70)
GRID_COLOR = (167, 209, 61)
FRAME_COLOR = (255, 255, 255)   # white outline
TEXT_COLOR = (255, 255, 255)    # white text

# ------------------ WINDOW ------------------
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 28)

# ------------------ SOUNDS ------------------
eat_sound = pygame.mixer.Sound("sounds/eat.mp3")
move_sound = pygame.mixer.Sound("sounds/move.mp3")
gameover_sound = pygame.mixer.Sound("sounds/gameover.mp3")

# ------------------ LOAD GRAPHICS ------------------
def load(name):
    return pygame.image.load(f"graphics/{name}").convert_alpha()

apple_img = load("apple.png")

head_up = load("head_up.png")
head_down = load("head_down.png")
head_left = load("head_left.png")
head_right = load("head_right.png")

tail_up = load("tail_up.png")
tail_down = load("tail_down.png")
tail_left = load("tail_left.png")
tail_right = load("tail_right.png")

body_vertical = load("body_vertical.png")
body_horizontal = load("body_horizontal.png")

body_topleft = load("body_topleft.png")
body_topright = load("body_topright.png")
body_bottomleft = load("body_bottomleft.png")
body_bottomright = load("body_bottomright.png")

def scale(img):
    return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

graphics = list(map(scale, [
    apple_img,
    head_up, head_down, head_left, head_right,
    tail_up, tail_down, tail_left, tail_right,
    body_vertical, body_horizontal,
    body_topleft, body_topright, body_bottomleft, body_bottomright
]))

(apple_img,
 head_up, head_down, head_left, head_right,
 tail_up, tail_down, tail_left, tail_right,
 body_vertical, body_horizontal,
 body_topleft, body_topright, body_bottomleft, body_bottomright) = graphics

# ------------------ GRID ------------------
grid_surface = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT), pygame.SRCALPHA)
for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        pygame.draw.rect(
            grid_surface,
            GRID_COLOR,
            (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
            1,
        )

# ------------------ SNAKE ------------------
class Snake:
    def __init__(self):
        self.body = [Vector2(7,7), Vector2(6,7), Vector2(5,7)]
        self.direction = Vector2(1,0)
        self.grow = False

    def draw(self):
        for i, block in enumerate(self.body):
            x = PLAY_X + block.x * TILE_SIZE
            y = PLAY_Y + block.y * TILE_SIZE
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            if i == 0:
                self.draw_head(rect)
            elif i == len(self.body) - 1:
                self.draw_tail(rect)
            else:
                self.draw_body(i, rect)

    def draw_head(self, rect):
        next_block = self.body[1] - self.body[0]
        if next_block == Vector2(1,0): screen.blit(head_left, rect)
        elif next_block == Vector2(-1,0): screen.blit(head_right, rect)
        elif next_block == Vector2(0,1): screen.blit(head_up, rect)
        else: screen.blit(head_down, rect)

    def draw_tail(self, rect):
        relation = self.body[-2] - self.body[-1]
        if relation == Vector2(1,0): screen.blit(tail_left, rect)
        elif relation == Vector2(-1,0): screen.blit(tail_right, rect)
        elif relation == Vector2(0,1): screen.blit(tail_up, rect)
        else: screen.blit(tail_down, rect)

    def draw_body(self, index, rect):
        prev = self.body[index + 1] - self.body[index]
        next = self.body[index - 1] - self.body[index]

        if prev.x == next.x:
            screen.blit(body_vertical, rect)
        elif prev.y == next.y:
            screen.blit(body_horizontal, rect)
        else:
            if (prev.x == -1 and next.y == -1) or (prev.y == -1 and next.x == -1):
                screen.blit(body_topleft, rect)
            elif (prev.x == -1 and next.y == 1) or (prev.y == 1 and next.x == -1):
                screen.blit(body_bottomleft, rect)
            elif (prev.x == 1 and next.y == -1) or (prev.y == -1 and next.x == 1):
                screen.blit(body_topright, rect)
            else:
                screen.blit(body_bottomright, rect)

    def move(self):
        return self.body[0] + self.direction

    def update(self, new_head):
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def check_tail_collision(self):
        return self.body[0] in self.body[2:]

# ------------------ FOOD ------------------
class Food:
    def __init__(self):
        self.randomize()

    def draw(self):
        rect = pygame.Rect(
            PLAY_X + self.pos.x * TILE_SIZE,
            PLAY_Y + self.pos.y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE,
        )
        screen.blit(apple_img, rect)

    def randomize(self):
        self.pos = Vector2(
            random.randint(0, GRID_SIZE-1),
            random.randint(0, GRID_SIZE-1)
        )

# ------------------ GAME ------------------
snake = Snake()
food = Food()
score = 0
game_over = False

running = True
while running:
    screen.fill(GREEN_BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            new_direction = None

            if event.key == pygame.K_UP and snake.direction.y != 1:
                new_direction = Vector2(0,-1)
            elif event.key == pygame.K_DOWN and snake.direction.y != -1:
                new_direction = Vector2(0,1)
            elif event.key == pygame.K_LEFT and snake.direction.x != 1:
                new_direction = Vector2(-1,0)
            elif event.key == pygame.K_RIGHT and snake.direction.x != -1:
                new_direction = Vector2(1,0)

            if new_direction:
                snake.direction = new_direction
                move_sound.play()

            if game_over and event.key == pygame.K_SPACE:
                snake = Snake()
                food = Food()
                score = 0
                game_over = False

    if not game_over:
        new_head = snake.move()

        # WALL COLLISION
        if (
            new_head.x < 0 or new_head.x >= GRID_SIZE or
            new_head.y < 0 or new_head.y >= GRID_SIZE
        ):
            gameover_sound.play()
            game_over = True
        else:
            snake.update(new_head)

            if snake.body[0] == food.pos:
                food.randomize()
                snake.grow = True
                score += 1
                eat_sound.play()

            if snake.check_tail_collision():
                gameover_sound.play()
                game_over = True

    # draw arena border
    pygame.draw.rect(
        screen,
        FRAME_COLOR,
        (PLAY_X-4, PLAY_Y-4, PLAY_WIDTH+8, PLAY_HEIGHT+8),
        border_radius=10,
        width=4
    )

    # arena background
    pygame.draw.rect(
        screen,
        GREEN_BG,
        (PLAY_X, PLAY_Y, PLAY_WIDTH, PLAY_HEIGHT)
    )

    screen.blit(grid_surface, (PLAY_X, PLAY_Y))
    food.draw()
    snake.draw()

    # SCORE TEXT
    score_text = font.render(f"SCORE: {score}", True, TEXT_COLOR)
    screen.blit(score_text,
                (WINDOW_WIDTH//2 - score_text.get_width()//2, PLAY_Y - 50))

    if game_over:
        over = font.render("GAME OVER - SPACE TO RESTART", True, TEXT_COLOR)
        screen.blit(over,
                    (WINDOW_WIDTH//2 - over.get_width()//2,
                     WINDOW_HEIGHT//2))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()