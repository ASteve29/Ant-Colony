import random

class Tile:
    def __init__(self):
        self.food = 0
        self.ant = 0
        self.pheromones = {
            "home": 0,
            "food": 0,
            "ant": 0
        }

class Ant:
    def __init__(self, pos):
        self.x, self.y = pos
        self.job = "scout"
        self.goal = "explore"
        self.health = 500
    def move(self, width, height):
        self.x = max(0, min(width - 1, self.x + random.randint(-1, 1)))
        self.y = max(0, min(height - 1, self.y + random.randint(-1, 1)))
        self.health -= 1

def diffuse_pheremones(grid, width, height):
    current_scents = [[grid[y][x].pheromones["home"] for x in range(width)] for y in range(height)]

    for y in range(height):
        for x in range(width):

            neighbor_sum = 0
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    neighbor_sum += current_scents[ny][nx]
            
            diff_factor = 0.2  # Lower is smoother
            evap_rate = 0.99999  # Lower = faster fading
            
            center_scent = current_scents[y][x]
            diffused = (center_scent * (1 - 4 * diff_factor)) + (neighbor_sum * diff_factor)
            
            grid[y][x].pheromones["home"] = diffused * evap_rate