import random
import pygame

colour_map = {
    "scout ant": (1, 0, 1),
    "forager ant": (0, 0, 1),
    "home": (0, 1, 0),
    "food": (1, 0.5, 0)
}

baseline_amount = 0.01
jobs = ["scout", "forager"]
goals = ["find food", "go home", "explore", "mate"]

pheromone_settings = {
    "home": {"diffusion": 0.2, "evaporation": 0.99999999},
    "food": {"diffusion": 0.15, "evaporation": 0.999},
    "forager ant": {"diffusion": 0.05, "evaporation": 0.98},
    "scout ant": {"diffusion": 0.05, "evaporation": 0.98}
}

goal_targets = {
    "find food": {"home": -0.1, "food": 1, "forager ant": 0.1, "scout ant": 0.1},
    "go home": {"home": 1, "food": 0.1, "forager ant": 0.2, "scout ant": 0.2},
    "explore": {"home": -1, "food": 0.1, "forager ant": 0.1, "scout ant": -0.5},
    "mate": {"home": 0.5, "food": 0.1, "forager ant": 1, "scout ant": 1}
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
                            pheromone_amount = grid[ny][nx].pheromones[scents] + baseline_amount * 10
                            weight = pheromone_amount * goal_targets[self.goal].get(scents, baseline_amount)
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
    pixels = pygame.PixelArray(surface)

    for y in range(height):
        for x in range(width):
            tile = grid[y][x]

            r, g, b = 0, 0, 0
            for pheromone, factor in colour_map.items():
                amount = tile.pheromones.get(pheromone, 0)
                max_display_value = 64
                r += min(amount / max_display_value, 1) * factor[0] * 255
                g += min(amount / max_display_value, 1) * factor[1] * 255
                b += min(amount / max_display_value, 1) * factor[2] * 255

            # clamp to 0–255
            r = min(255, int(r + tile.ant * 75))
            g = min(255, int(g))
            b = min(255, int(b))
            pixels[x, y] = (r, g, b)

    del pixels