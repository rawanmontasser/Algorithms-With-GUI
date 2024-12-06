
import pygame
import random
import heapq
import time
from collections import deque
from colorama import Fore, Style, init

init(autoreset=True)

pygame.init()

TILE_COLOR_1 = (60, 90, 150, 255)
TILE_COLOR_2 = (90, 120, 180, 255)
TILE_COLOR_3 = (150, 160, 190, 255)
EMPTY_TILE_COLOR = (150, 160, 190, 255)
BORDER_COLOR = (30, 40, 60, 255)
BUTTON_COLOR = (50, 80, 120, 255)
BACKGROUND_COLOR = (20, 20, 30, 255)
TEXT_COLOR = (210, 210, 210, 255)

SCREEN_WIDTH = 630
SCREEN_HEIGHT = 396
GRID_SIZE = 3
TILE_SIZE = 125
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 40
FONT = pygame.font.SysFont('Arial', 26, bold=True)

GOAL_STATE = [1, 2, 3, 4, 5, 6, 7, 8, 0]
GOAL_TUPLE = tuple(GOAL_STATE)

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
MOVE_NAMES = ['UP', 'DOWN', 'LEFT', 'RIGHT']

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('8-Puzzle Solver')

initial_state = []
solution_path = None
steps = 0
start_time = 0
execution_time = 0
is_solving = False

def index_to_position(index):
    return (index // 3, index % 3)

def is_goal(state):
    return tuple(state) == GOAL_TUPLE

def get_neighbors(state):
    neighbors = []
    zero_index = state.index(0)
    zero_row, zero_col = index_to_position(zero_index)

    for dr, dc in MOVES:
        new_row, new_col = zero_row + dr, zero_col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            new_state = state[:]
            new_state[zero_index], new_state[new_index] = new_state[new_index], new_state[zero_index]
            neighbors.append((new_state, MOVE_NAMES[MOVES.index((dr, dc))]))

    return neighbors

def bfs(initial_state):
    visited = set()
    queue = deque([(initial_state, [], None)])

    while queue:
        current_state, path, last_move = queue.popleft()
        if is_goal(current_state):
            return path
        
        visited.add(tuple(current_state))
        for neighbor, move in get_neighbors(current_state):
            if tuple(neighbor) not in visited:
                queue.append((neighbor, path + [(neighbor, move)], move))

    return None

def iterative_deepening_dfs(initial_state, max_depth_increment=1):
    depth = 0
    while True:
        solution = dfs(initial_state, depth)
        if solution is not None:
            return solution
        depth += max_depth_increment
        if depth > 1500:
            print("Maximum depth reached without finding a solution.")
            break
    return None

 

def dfs(initial_state, max_depth=30):
    stack = [(initial_state, [], None, 0)]
    visited = set()
    
    while stack:
        current_state, path, last_move, depth = stack.pop()

        if is_goal(current_state):
            return path

        state_tuple = tuple(current_state)
        if state_tuple not in visited:
            visited.add(state_tuple)

            if depth < max_depth:
                neighbors = get_neighbors(current_state)

                for neighbor, move in reversed(neighbors):
                    if tuple(neighbor) not in visited:
                        stack.append((neighbor, path + [(neighbor, move)], move, depth + 1))

    return None

def ucs(initial_state):
    visited = set()
    queue = []
    heapq.heappush(queue, (0, initial_state, [], None))

    while queue:
        cost, current_state, path, last_move = heapq.heappop(queue)
        if is_goal(current_state):
            return path
        
        visited.add(tuple(current_state))
        for neighbor, move in get_neighbors(current_state):
            if tuple(neighbor) not in visited:
                new_cost = cost + 1
                heapq.heappush(queue, (new_cost, neighbor, path + [(neighbor, move)], move))

    return None

def draw_board(state):
    offset_x = 10
    offset_y = 10

    for i in range(9):
        row, col = index_to_position(i)  
        number = state[i]
        
        x_pos = col * TILE_SIZE + offset_x
        y_pos = row * TILE_SIZE + offset_y
        
        if number != 0:
            pygame.draw.rect(screen, TILE_COLOR_1, (x_pos, y_pos, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, BORDER_COLOR, (x_pos, y_pos, TILE_SIZE, TILE_SIZE), 3)
            text = FONT.render(str(number), True, TEXT_COLOR)
            screen.blit(text, (x_pos + TILE_SIZE // 2 - text.get_width() // 2, y_pos + TILE_SIZE // 2 - text.get_height() // 2))
        else:
            pygame.draw.rect(screen, TILE_COLOR_2, (x_pos, y_pos, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, BORDER_COLOR, (x_pos, y_pos, TILE_SIZE, TILE_SIZE), 3)
    
    if is_solving:
        running_time_text = FONT.render(f"   Time: {time.time() - start_time:.1f}s", True, TEXT_COLOR)
        steps_text = FONT.render(f"Steps Taken: {steps}", True, TEXT_COLOR)
    else:
        running_time_text = FONT.render(f"   Time: {execution_time:.1f}s", True, TEXT_COLOR)
        steps_text = FONT.render(f"Steps Taken: {steps}", True, TEXT_COLOR)
    
    screen.blit(running_time_text, (SCREEN_WIDTH - 200, 275))
    screen.blit(steps_text, (SCREEN_WIDTH - 200, 300))

def draw_buttons():
    new_game_button = pygame.Rect(SCREEN_WIDTH - BUTTON_WIDTH - 40, 45, BUTTON_WIDTH, BUTTON_HEIGHT)
    bfs_button = pygame.Rect(SCREEN_WIDTH - BUTTON_WIDTH - 40, 95, BUTTON_WIDTH, BUTTON_HEIGHT)
    dfs_button = pygame.Rect(SCREEN_WIDTH - BUTTON_WIDTH - 40, 145, BUTTON_WIDTH, BUTTON_HEIGHT)
    ucs_button = pygame.Rect(SCREEN_WIDTH - BUTTON_WIDTH - 40, 195, BUTTON_WIDTH, BUTTON_HEIGHT)

    pygame.draw.rect(screen, BUTTON_COLOR, new_game_button)
    pygame.draw.rect(screen, BUTTON_COLOR, bfs_button)
    pygame.draw.rect(screen, BUTTON_COLOR, dfs_button)
    pygame.draw.rect(screen, BUTTON_COLOR, ucs_button)

    new_game_text = FONT.render("New Game", True, TEXT_COLOR)
    bfs_text = FONT.render("BFS", True, TEXT_COLOR)
    dfs_text = FONT.render("DFS", True, TEXT_COLOR)
    ucs_text = FONT.render("UCS", True, TEXT_COLOR)

    screen.blit(new_game_text, (new_game_button.centerx - new_game_text.get_width() // 2, new_game_button.centery - new_game_text.get_height() // 2))
    screen.blit(bfs_text, (bfs_button.centerx - bfs_text.get_width() // 2, bfs_button.centery - bfs_text.get_height() // 2))
    screen.blit(dfs_text, (dfs_button.centerx - dfs_text.get_width() // 2, dfs_button.centery - dfs_text.get_height() // 2))
    screen.blit(ucs_text, (ucs_button.centerx - ucs_text.get_width() // 2, ucs_button.centery - ucs_text.get_height() // 2))

    return new_game_button, bfs_button, dfs_button, ucs_button

def generate_new_game():
    state = list(range(9))
    random.shuffle(state)
    while not is_solvable(state):
        random.shuffle(state)
    return state

def is_solvable(state):
    inversions = 0
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            if state[i] > state[j] and state[i] != 0 and state[j] != 0:
                inversions += 1
    return inversions % 2 == 0

def start_solving(path):
    global is_solving, steps, execution_time, start_time, initial_state
    is_solving = True
    steps = 0
    start_time = time.time()
    
    for state, move in path:
        screen.fill(BACKGROUND_COLOR)
        steps += 1 
        pygame.time.wait(500)
        draw_board(state)
        draw_buttons()
        pygame.display.flip()

    initial_state = path[-1][0]
    execution_time = time.time() - start_time
    is_solving = False

def game_loop():
    global initial_state, solution_path, is_solving, steps, execution_time
    clock = pygame.time.Clock()
    running = True

    new_game_button, bfs_button, dfs_button, ucs_button = draw_buttons()

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_board(initial_state)

        draw_buttons()

        if is_solving:
            pygame.display.flip()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if new_game_button.collidepoint(event.pos):
                        initial_state = generate_new_game()
                        execution_time = 0
                        steps = 0
                        solution_path = None
                    elif bfs_button.collidepoint(event.pos) and not is_goal(initial_state):
                        solution_path = bfs(initial_state)
                        start_solving(solution_path)
                    elif dfs_button.collidepoint(event.pos) and not is_goal(initial_state):
                        solution_path = iterative_deepening_dfs(initial_state)
                        start_solving(solution_path)
                    elif ucs_button.collidepoint(event.pos) and not is_goal(initial_state):
                        solution_path = ucs(initial_state)
                        start_solving(solution_path)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == '__main__':
    initial_state = generate_new_game()

    print(Fore.BLUE + "\nWelcome to the 8 puzzle solver!\n")
    game_loop()

