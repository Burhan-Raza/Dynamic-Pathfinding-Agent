import pygame
import heapq
import time
import random
import math
from collections import deque


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)


class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_obstacle = False
        self.is_start = False
        self.is_goal = False
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f


class PathfindingApp:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont(None, 24)
        self.screen = None
        self.grid = []
        self.rows = 0
        self.cols = 0
        self.cell_size = 10  # Reduced from 20 to allow larger grids
        self.start = None
        self.goal = None
        self.algorithm = 'A*'
        self.heuristic = 'Manhattan'
        self.dynamic_mode = False
        self.obstacle_prob = 0.01 
        self.obstacle_density = 0.3
        self.running = True
        self.editing = False
        self.searching = False
        self.path = []
        self.metrics = {'nodes_visited': 0, 'path_cost': 0, 'exec_time': 0}
        self.setup_menu()

    def setup_menu(self):
        self.screen = pygame.display.set_mode((400, 400))
        pygame.display.set_caption("Pathfinding Setup")
        input_fields = {'rows': '', 'cols': '', 'density': ''}
        current_field = 'rows'
        
        while True:
            self.screen.fill(WHITE)
            self.draw_text("Grid Configuration", 50, 30)
            self.draw_text("Rows (default 50):", 50, 80)
            self.draw_text("Columns (default 80):", 50, 130)
            self.draw_text("Obstacle Density (0-1, default 0.3):", 50, 180)
            self.draw_text("Press ENTER to next field, ESC to start", 50, 250)
            
            # Display current input fields
            self.draw_text(input_fields['rows'] or '50', 250, 80)
            self.draw_text(input_fields['cols'] or '80', 250, 130)
            self.draw_text(input_fields['density'] or '0.3', 250, 180)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        try:
                            self.rows = int(input_fields['rows']) if input_fields['rows'] else 50
                            self.cols = int(input_fields['cols']) if input_fields['cols'] else 80
                            self.obstacle_density = float(input_fields['density']) if input_fields['density'] else 0.3
                            
                            if self.rows > 0 and self.cols > 0 and 0 <= self.obstacle_density <= 1:
                                self.initialize_grid()
                                self.select_start_goal()
                                self.main_loop()
                                return
                        except ValueError:
                            pass
                    elif event.key == pygame.K_RETURN:
                        fields = list(input_fields.keys())
                        current_idx = fields.index(current_field)
                        current_field = fields[(current_idx + 1) % len(fields)]
                    elif event.key == pygame.K_BACKSPACE:
                        input_fields[current_field] = input_fields[current_field][:-1]
                    else:
                        input_fields[current_field] += event.unicode

    def initialize_grid(self):
        self.grid = [[Node(i, j) for j in range(self.cols)] for i in range(self.rows)]
        screen_width = self.cols * self.cell_size + 250
        screen_height = self.rows * self.cell_size
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(f"Dynamic Pathfinding Agent ({self.rows}x{self.cols})")

    def select_start_goal(self):
        selecting_start = True
        selecting_goal = False
        while True:
            self.draw_grid()
            self.draw_sidebar()
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if pos[0] < self.cols * self.cell_size:
                        row = pos[1] // self.cell_size
                        col = pos[0] // self.cell_size
                        if 0 <= row < self.rows and 0 <= col < self.cols:
                            if selecting_start:
                                self.start = self.grid[row][col]
                                self.start.is_start = True
                                selecting_start = False
                                selecting_goal = True
                            elif selecting_goal:
                                self.goal = self.grid[row][col]
                                self.goal.is_goal = True
                                return

    def main_loop(self):
        self.editing = True
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.draw_grid()
            self.draw_sidebar()
            pygame.display.flip()
            if self.searching:
                self.perform_search()
            if self.dynamic_mode and self.path:
                self.simulate_movement()
            clock.tick(60)  # 60 FPS cap

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[0] < self.cols * self.cell_size:
                    if self.editing:
                        row = pos[1] // self.cell_size
                        col = pos[0] // self.cell_size
                        if 0 <= row < self.rows and 0 <= col < self.cols:
                            node = self.grid[row][col]
                            if not node.is_start and not node.is_goal:
                                node.is_obstacle = not node.is_obstacle
                else:
                    button_height = 30
                    sidebar_x = self.cols * self.cell_size
                    if sidebar_x < pos[0] < sidebar_x + 250:
                        if 50 < pos[1] < 50 + button_height:
                            self.generate_random_map()
                        elif 100 < pos[1] < 100 + button_height:
                            self.editing = not self.editing
                        elif 150 < pos[1] < 150 + button_height:
                            self.algorithm = 'A*' if self.algorithm == 'GBFS' else 'GBFS'
                        elif 200 < pos[1] < 200 + button_height:
                            self.heuristic = 'Manhattan' if self.heuristic == 'Euclidean' else 'Euclidean'
                        elif 250 < pos[1] < 250 + button_height:
                            self.dynamic_mode = not self.dynamic_mode
                        elif 300 < pos[1] < 300 + button_height:
                            self.searching = True
                        elif 350 < pos[1] < 350 + button_height:
                            self.reset_grid()

    def draw_grid(self):
        self.screen.fill(WHITE)
        for row in range(self.rows):
            for col in range(self.cols):
                node = self.grid[row][col]
                color = WHITE
                if node.is_obstacle:
                    color = BLACK
                elif node.is_start:
                    color = GREEN
                elif node.is_goal:
                    color = RED
                pygame.draw.rect(self.screen, color, (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size))
                if self.cell_size > 8:  # Only draw grid lines if cells are big enough
                    pygame.draw.rect(self.screen, GRAY, (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size), 1)

        for node in self.path:
            pygame.draw.rect(self.screen, GREEN, (node.col * self.cell_size, node.row * self.cell_size, self.cell_size, self.cell_size))

    def draw_sidebar(self):
        sidebar_x = self.cols * self.cell_size
        pygame.draw.rect(self.screen, GRAY, (sidebar_x, 0, 250, self.screen.get_height()))
        
        buttons = [
            ("Generate Map", 50),
            ("Toggle Edit", 100),
            (f"Algorithm: {self.algorithm}", 150),
            (f"Heuristic: {self.heuristic}", 200),
            (f"Dynamic: {self.dynamic_mode}", 250),
            ("Start Search", 300),
            ("Reset", 350)
        ]
        
        for text, y in buttons:
            self.draw_text(text, sidebar_x + 10, y)
        
        self.draw_text("Metrics:", sidebar_x + 10, 410)
        self.draw_text(f"Nodes Visited: {self.metrics['nodes_visited']}", sidebar_x + 10, 440)
        self.draw_text(f"Path Cost: {self.metrics['path_cost']}", sidebar_x + 10, 470)
        self.draw_text(f"Exec Time: {self.metrics['exec_time']} ms", sidebar_x + 10, 500)

    def draw_text(self, text, x, y):
        img = self.font.render(str(text), True, BLACK)
        self.screen.blit(img, (x, y))

    def generate_random_map(self):
        for row in range(self.rows):
            for col in range(self.cols):
                node = self.grid[row][col]
                if not node.is_start and not node.is_goal:
                    node.is_obstacle = random.random() < self.obstacle_density

    def reset_grid(self):
        self.path = []
        self.metrics = {'nodes_visited': 0, 'path_cost': 0, 'exec_time': 0}
        for row in self.grid:
            for node in row:
                node.g = float('inf')
                node.h = 0
                node.f = float('inf')
                node.parent = None

    def get_neighbors(self, node):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = node.row + dr, node.col + dc
            if 0 <= r < self.rows and 0 <= c < self.cols:
                neighbor = self.grid[r][c]
                if not neighbor.is_obstacle:
                    neighbors.append(neighbor)
        return neighbors

    def calculate_heuristic(self, node):
        if self.heuristic == 'Manhattan':
            return abs(node.row - self.goal.row) + abs(node.col - self.goal.col)
        else:  # Euclidean
            return math.sqrt((node.row - self.goal.row)**2 + (node.col - self.goal.col)**2)

    def perform_search(self):
        self.searching = False
        self.reset_grid()
        start_time = time.time()
        
        open_set = []
        closed_set = set()
        self.start.g = 0
        self.start.h = self.calculate_heuristic(self.start)
        
        # Key difference: A* uses f = g + h, GBFS uses f = h only
        if self.algorithm == 'A*':
            self.start.f = self.start.g + self.start.h
        else:  # GBFS
            self.start.f = self.start.h
        
        heapq.heappush(open_set, self.start)
        
        visited = 0
        
        while open_set:
            current = heapq.heappop(open_set)
            visited += 1
            
            if current == self.goal:
                self.reconstruct_path(current)
                break
            
            if current in closed_set:
                continue
            
            closed_set.add(current)
            
            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                tentative_g = current.g + 1
                
                if tentative_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = tentative_g
                    neighbor.h = self.calculate_heuristic(neighbor)
                    
                    # Proper A* vs GBFS logic
                    if self.algorithm == 'A*':
                        neighbor.f = neighbor.g + neighbor.h
                    else:  # GBFS - only uses heuristic
                        neighbor.f = neighbor.h
                    
                    if neighbor not in open_set:
                        heapq.heappush(open_set, neighbor)
            
            # Visualization
            if current != self.start and current != self.goal:
                pygame.draw.rect(self.screen, BLUE, (current.col * self.cell_size, current.row * self.cell_size, self.cell_size, self.cell_size))
            for node in open_set:
                if node != self.start and node != self.goal:
                    pygame.draw.rect(self.screen, YELLOW, (node.col * self.cell_size, node.row * self.cell_size, self.cell_size, self.cell_size))
            pygame.display.flip()
            time.sleep(0.01)  # Reduced sleep for larger grids
        
        exec_time = (time.time() - start_time) * 1000
        self.metrics = {'nodes_visited': visited, 'path_cost': len(self.path), 'exec_time': round(exec_time, 2)}

    def reconstruct_path(self, current):
        self.path = []
        while current:
            self.path.append(current)
            current = current.parent
        self.path.reverse()

    def simulate_movement(self):
        if not self.path:
            return
        
        current_pos = self.path[0]
        self.path.pop(0)
        
        # Add random obstacles
        if random.random() < self.obstacle_prob:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            node = self.grid[row][col]
            if not node.is_obstacle and not node.is_start and not node.is_goal and node not in self.path:
                node.is_obstacle = True
        
        # Check if path is blocked
        blocked = False
        for node in self.path:
            if node.is_obstacle:
                blocked = True
                break
        
        if blocked:
            self.start = current_pos
            self.start.is_start = True
            self.perform_search()
        
        pygame.draw.rect(self.screen, GREEN, (current_pos.col * self.cell_size, current_pos.row * self.cell_size, self.cell_size, self.cell_size))
        pygame.display.flip()
        time.sleep(0.5)

    def quit(self):
        pygame.quit()
        self.running = False

if __name__ == "__main__":
    app = PathfindingApp()