import pygame
import random
import sqlite3

pygame.init()

WIDTH, HEIGHT = 600, 500
GRID_SIZE = 20
WHITE, GREEN, YELLOW, PURPLE, PINK = (255, 255, 255), (135, 194, 138), (250, 209, 0), (129, 11, 84), (239, 12, 148)
FONT = pygame.font.Font(None, 30)

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

conn = sqlite3.connect("scores.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        score INTEGER
    )
""")
conn.commit()

def save_score(score):
    """Saves the score to the database."""
    c.execute("INSERT INTO scores (score) VALUES (?)", (score,))
    conn.commit()

def get_top_scores():
    """Retrieves the top 10 highest scores."""
    c.execute("SELECT score FROM scores ORDER BY score DESC LIMIT 10")
    return [row[0] for row in c.fetchall()]

def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(win, GREEN, (*segment, GRID_SIZE, GRID_SIZE), border_radius=5)

def draw_food(food):
    pygame.draw.rect(win, YELLOW, (*food, GRID_SIZE, GRID_SIZE), border_radius=5)

def draw_text(text, x, y, color=WHITE):
    label = FONT.render(text, True, color)
    win.blit(label, (x, y))

def show_leaderboard():
    win.fill(PURPLE)
    draw_text("Top 10 Best Scores:", WIDTH // 2 - 80, 50, PINK)
    top_scores = get_top_scores()
    for i, score in enumerate(top_scores, start=1):
        draw_text(f"{i}. {score}", WIDTH // 2 - 30, 80 + i * 25, WHITE)
    draw_text("Press B to go back", WIDTH // 2 - 60, HEIGHT - 40, YELLOW)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_b]:
            return

def game_loop():
    snake = [(100, 100), (80, 100), (60, 100)]
    snake_dir = (GRID_SIZE, 0)
    food = (random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
            random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE)
    score = 0
    running = True
    game_over = False

    clock = pygame.time.Clock()

    while running:
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and snake_dir != (0, GRID_SIZE):
            snake_dir = (0, -GRID_SIZE)
        if keys[pygame.K_DOWN] and snake_dir != (0, -GRID_SIZE):
            snake_dir = (0, GRID_SIZE)
        if keys[pygame.K_LEFT] and snake_dir != (GRID_SIZE, 0):
            snake_dir = (-GRID_SIZE, 0)
        if keys[pygame.K_RIGHT] and snake_dir != (-GRID_SIZE, 0):
            snake_dir = (GRID_SIZE, 0)
        if keys[pygame.K_t]:
            show_leaderboard()

        if not game_over:
            new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
            snake.insert(0, new_head)

            if new_head == food:
                score += 1
                food = (random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
                        random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE)
            else:
                snake.pop()

            if (new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT or
                new_head in snake[1:]):
                game_over = True
                save_score(score)

        win.fill(PURPLE)
        draw_snake(snake)
        draw_food(food)
        draw_text(f"Score: {score}", 10, 10)
        draw_text("Press T for Top Scores", WIDTH - 170, 10, PINK)

        if game_over:
            draw_text("GAME OVER!", WIDTH // 2 - 60, HEIGHT // 2 - 30, YELLOW)
            draw_text("Press 'R' to Restart", WIDTH // 2 - 80, HEIGHT // 2, PINK)
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                return game_loop()

        pygame.display.update()

game_loop()
conn.close()
pygame.quit()