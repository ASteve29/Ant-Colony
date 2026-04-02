import random

pheromone_settings = {
    "home": {
        "diffusion": 0.2,
        "evaporation": 0.99999
    },
    "food": {
        "diffusion": 0.15,
        "evaporation": 0.999
    },
    "forager ant": {
        "diffusion": 0.05,
        "evaporation": 0.98
    },
    "scout ant": {
        "diffusion": 0.05,
        "evaporation": 0.98
    }
}

# Classes

class Tile:
    def __init__(self):
        self.food = 0
        self.ant = 0
        self.pheromones = {
            "home": 0,
            "food": 0,
            "forager ant": 0,
            "scout ant": 0
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

# Functions

def diffuse_pheremones(grid, width, height):
    for scents in phermemone_settings:
    	current_scents = [[grid[y][x].pheromones[scents] for x in range(width)] for y in range(height)]
	
	    for y in range(height):
	        for x in range(width):
	
	            neighbor_sum = 0
	            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
	                nx, ny = x + dx, y + dy
	                if 0 <= nx < width and 0 <= ny < height:
	                    neighbor_sum += current_scents[ny][nx]
	            
	            diff_factor = pheromone_settings[scents]["diffusion"]
	            evap_rate = pheromone_settings[scents]["evaporation"]
	            
	            
	            center_scent = current_scents[y][x]
	            diffused = (center_scent * (1 - 4 * diff_factor)) + (neighbor_sum * diff_factor)
	            
	            grid[y][x].pheromones[scents] = diffused * evap_rate