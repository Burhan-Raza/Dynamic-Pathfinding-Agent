import heapq

class AStar:
    def __init__(self, start, goal, grid):
        self.start = start
        self.goal = goal
        self.grid = grid
        self.open_set = []
        self.closed_set = set()
        self.came_from = {}
        self.g_score = {start: 0}
        self.f_score = {start: self.heuristic(start)}
        self.counter = 0  # Tiebreaker

    def heuristic(self, node):
        return abs(node[0] - self.goal[0]) + abs(node[1] - self.goal[1])

    def get_neighbors(self, node):
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for direction in directions:
            neighbor = (node[0] + direction[0], node[1] + direction[1])
            if neighbor in self.grid:
                neighbors.append(neighbor)
        return neighbors

    def reconstruct_path(self, current):
        total_path = [current]
        while current in self.came_from:
            current = self.came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def execute(self):
        heapq.heappush(self.open_set, (self.f_score[self.start], self.counter, self.start))
        self.counter += 1

        while self.open_set:
            current = heapq.heappop(self.open_set)[2]

            if current == self.goal:
                return self.reconstruct_path(current)

            self.closed_set.add(current)
            for neighbor in self.get_neighbors(current):
                if neighbor in self.closed_set:
                    continue
                tentative_g_score = self.g_score[current] + 1  # Assume cost = 1
                if neighbor not in self.g_score:
                    self.g_score[neighbor] = float('inf')
                if tentative_g_score < self.g_score[neighbor]:
                    self.came_from[neighbor] = current
                    self.g_score[neighbor] = tentative_g_score
                    self.f_score[neighbor] = tentative_g_score + self.heuristic(neighbor)
                    if (self.f_score[neighbor], self.counter, neighbor) not in self.open_set:
                        heapq.heappush(self.open_set, (self.f_score[neighbor], self.counter, neighbor))
                        self.counter += 1
        return []  # No path found

# Example usage of the AStar class
# grid = [(x, y), ...]  # Define your grid as a set of walkable nodes.
# start = (0, 0)  # Starting point
# goal = (5, 5)  # Goal point
# a_star = AStar(start, goal, grid)
# path = a_star.execute()
# print(path)  # Output the path found