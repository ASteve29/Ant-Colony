import random
import pygame

baseline_amount = 0.01
jobs = ["scout", "forager"]
goals = ["find food", "go home", "explore", "mate"]

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

goal_targets = {
    "find food": {
        "home": {
            "weight": 0
        },
        "food": {
            "weight": 1
        },
        "forager ant": {
            "weight": 0.1
        },
        "scout ant": {
            "weight": 0.1
        }
    },
    "go home": {
        "home": {
            "weight": 1
        },
        "food": {
            "weight": 0.1
        },
        "forager ant": {
            "weight": 0.2
        },
        "scout ant": {
            "weight": 0.2
        }
    },
    "explore": {
        "home": {
            "weight": -1
        },
        "food": {
            "weight": 0.1
        },
        "forager ant": {
            "weight": 0.1
        },
        "scout ant": {
            "weight":-0.5
        }
    },
    "mate": {
        "home": {
            "weight": 0.5
        },
        "food": {
            "weight": 0.1
        },
        "forager ant": {
            "weight": 1
        },
        "scout ant": {
            "weight": 1
        }
    }
}

# Classes
class Tile:
    def __init__(self):
        self.food = 0
        self.ant = 0
        self.pheromones = {
            "home": 0.0,
            "food": 0.0,
            "forager ant": 0.0,
            "scout ant": 0.0
        }

class Ant:
    def __init__(self, pos):
        self.x, self.y = pos
        self.job = "scout"
        self.goal = "explore"
        self.health = 500
        
    def move(self, grid, width, height):
        options = []
        weights = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    nx = self.x + dx
                    ny = self.y + dy

                    if 0 <= nx < width and 0 <= ny < height:
                        options.append((nx, ny))

                        total_score = 0
                        for scents in pheromone_settings:
                            pheremone_amount = grid[ny][nx].pheromones[scents] + baseline_amount

                            weight = pheremone_amount * goal_targets[self.goal][scents]["weight"]
                            total_score += weight
                        
                        weights.append(max(baseline_amount, total_score))
        self.x, self.y = random.choices(options, weights=weights, k=1)[0]

        self.health -= 1





# Functions
def diffuse_pheromones(grid, width, height):
    for scent in pheromone_settings:
        current_scents = [[grid[y][x].pheromones[scent] for x in range(width)] for y in range(height)]
        
        diff_factor = pheromone_settings[scent]["diffusion"]
        evap_rate = pheromone_settings[scent]["evaporation"]
    
        for y in range(height):
            for x in range(width):
                neighbor_sum = 0
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor_sum += current_scents[ny][nx]
                
                center_scent = current_scents[y][x]
                diffused = (center_scent * (1 - 4 * diff_factor)) + (neighbor_sum * diff_factor)
                
                grid[y][x].pheromones[scent] = diffused * evap_rate




def draw_grid(surface, grid, width, height):
    surface.fill((0, 0, 0))
    
    # Open the PixelArray to lock the surface for fast editing
    pixels = pygame.PixelArray(surface)
    
    for y in range(height):
        for x in range(width):
            tile = grid[y][x]
            
            # Map different layers to RGB channels for visualization
            if tile.pheromones["home"] > 0.1 or tile.ant > 0 or tile.pheromones["food"] > 0.1:
                red = min(255, tile.ant * 75)
                green = min(255, int(tile.pheromones["home"] * 4))
                blue = min(255, int(tile.pheromones["food"] * 4))
                
                pixels[x, y] = (red, green, blue)
                
    # Unlock the surface so Pygame can scale it
    del pixels 
