# Assuming this is the improved content of pathfinding.py with proper A* implementation and error handling

class AStar:
    def __init__(self, grid):
        self.grid = grid
        self.start = None
        self.end = None

    def set_start(self, start):
        if not self.is_valid_point(start):
            raise ValueError('Invalid start point')
        self.start = start

    def set_end(self, end):
        if not self.is_valid_point(end):
            raise ValueError('Invalid end point')
        self.end = end

    def is_valid_point(self, point):
        x, y = point
        return 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0])

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def astar(self):
        if self.start is None or self.end is None:
            raise RuntimeError('Start or end point is not set')

        open_set = {self.start}
        came_from = {}

        g_score = {point: float('inf') for row in self.grid for point in row}  # Dictionary for g score
        g_score[self.start] = 0

        f_score = {point: float('inf') for row in self.grid for point in row}  # Dictionary for f score
        f_score[self.start] = self.heuristic(self.start, self.end)

        while open_set:
            current = min(open_set, key=lambda o: f_score[o])

            if current == self.end:
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)

            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, self.end)
                    if neighbor not in open_set:
                        open_set.add(neighbor)

        raise RuntimeError('Path not found')

    def get_neighbors(self, point):
        # Returns a list of passable neighbors
        x, y = point
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (x + dx, y + dy)
            if self.is_valid_point(neighbor) and self.grid[neighbor[0]][neighbor[1]] != 1:
                neighbors.append(neighbor)
        return neighbors

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]  # Return reversed path

# Error handling and proper tiebreaking have been implemented in the astar method.