import random
import pygame
import numpy as np
from scipy.ndimage import convolve

FOOD = 0
ANT = 1
P_HOME = 2
P_FOOD = 3
P_FORAGER = 4
P_SCOUT = 5

P_MAP = {
    "home": P_HOME,
    "food": P_FOOD,
    "forager ant": P_FORAGER,
    "scout ant": P_SCOUT
}

baseline_amount = 0.01
jobs = [P_SCOUT, P_FORAGER]
goals = ["find food", "go home", "explore", "mate"]

evap_rates = [0.99999999, 0.99, 0.9, 0.9]
diffuse_rates = [0.2, 0.015, 0.05, 0.05]

goal_targets = {
    "find food": {"home": -30, "food": 3, "forager ant": 0.1, "scout ant": 0.1},
    "go home": {"home": 500, "food": 0.01, "forager ant": 0, "scout ant": 0},
    "explore": {"home": -5, "food": 0.1, "forager ant": 0, "scout ant": 0.1},
    "mate": {"home": 0.5, "food": 0.1, "forager ant": 1, "scout ant": 1}
}

# Classes

class Ant:
    def __init__(self, pos, spawn_range):
        self.x = pos[0] + random.randint(-spawn_range, spawn_range)
        self.y = pos[1] + random.randint(-spawn_range, spawn_range)
        self.job = P_SCOUT
        self.goal = "explore"
        self.health = 1000
        self.food = 0
        self.trail_strength = 0

    def move(self, grid, width, height):
        # 1. Food Sensing (Index 0)
        if grid[self.x, self.y, FOOD] > 0:
            self.food += 1
            self.health += 10
            self.job = P_FORAGER
            self.goal = "go home"
            self.trail_strength += 10 * self.food
            grid[self.x, self.y, FOOD] -= 1

        # 2. Dropping Pheromones
        if self.goal == "go home" and self.job == P_FORAGER:
            grid[self.x, self.y, P_FOOD] += (self.trail_strength / 10) * (self.health / 500)
            self.trail_strength *= 0.99
            if grid[self.x, self.y, P_HOME] > 32:
                self.health += 50 * self.food
                self.food = 0
                self.goal = "find food"
                self.trail_strength += 100
        elif self.goal in ["find food", "explore"]:
            grid[self.x, self.y, P_HOME] += self.health/500 + (self.trail_strength / 10)
        
        # Job-specific scent
        scent_idx = P_FORAGER if self.job == P_FORAGER else P_SCOUT
        grid[self.x, self.y, scent_idx] += 5 * (self.health/500)

        # 3. Changing Jobs
        if self.job == P_SCOUT and grid[self.x, self.y, P_SCOUT] > 10:
            new_job = random.choices(jobs, weights=[100, grid[self.x, self.y, P_SCOUT]/10])[0]
            if new_job != self.job:
                self.job = new_job
                self.goal = "find food"

        # 2. Forager to Scout transition
        if self.job == P_FORAGER and grid[self.x, self.y, P_FORAGER] > 10:
            new_job = random.choices(jobs, weights=[grid[self.x, self.y, P_FORAGER]/10, 100])[0]
            if new_job != self.job:
                self.job = new_job
                self.goal = "explore"

        # 4. Decision Making (The weighted choice)
        options = []
        weights = []
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < width and 0 <= ny < height:
                options.append((nx, ny))
                
                # Calculate score using goal_targets and P_MAP
                total_score = 0
                for name, target_weight in goal_targets[self.goal].items():
                    layer_idx = P_MAP[name]
                    val = grid[nx, ny, layer_idx] + (baseline_amount * 10)
                    total_score += val * target_weight
                weights.append(max(0.1, total_score)) # Keep it positive

        self.x, self.y = random.choices(options, weights=weights, k=1)[0]
        self.health -= 1
        

# Functions
def diffuse_pheromones(grid, width, height): # High value = spreads faster

    for i in range(len(evap_rates)):
        rate = evap_rates[i]
        diff = diffuse_rates[i]
        
        # Ensure the total sum of the kernel equals the evaporation rate
        center = rate - diff
        side = diff / 8
        
        kernel = np.array([
            [side, side, side],
            [side, center, side],
            [side, side, side]
        ])
        
        # Apply to the correct layer (starting at index 2)
        grid[:, :, i + 2] = convolve(grid[:, :, i + 2], kernel, mode='constant')

def draw_grid(surface, grid):
    # 1. Create an empty RGB array (Width x Height x 3)
    # Use float32 for calculations to avoid rounding errors during math
    rgb = np.zeros((grid.shape[0], grid.shape[1], 3), dtype=np.float32)

    # 2. Apply your colour_map logic using NumPy layers
    # Scout Ant Pheromone (Layer 5) -> (3, 0, 3)
    scout_ant = grid[:, :, P_SCOUT]
    rgb[:, :, 0] += scout_ant * 3
    rgb[:, :, 2] += scout_ant * 3

    # Forager Ant Pheromone (Layer 4) -> (0, 3, 3)
    forager_ant = grid[:, :, P_FORAGER]
    rgb[:, :, 1] += forager_ant * 3
    rgb[:, :, 2] += forager_ant * 3

    # Home Pheromone (Layer 2) -> (0, 2, 0)
    home_ant = grid[:, :, P_HOME]
    rgb[:, :, 1] += home_ant * 2

    # Food Pheromone (Layer 3) -> (2, 2, 0)
    food_p_ant = grid[:, :, P_FOOD]
    rgb[:, :, 0] += food_p_ant * 2
    rgb[:, :, 1] += food_p_ant * 2

    # 3. Add the actual Food and Ants (the "Physical" layers)
    # You used + tile.ant * 100 + tile.food * 10 in your original code
    rgb[:, :, 0] += grid[:, :, ANT] * 100 + grid[:, :, FOOD] * 75
    rgb[:, :, 1] += grid[:, :, FOOD] * 35
    rgb[:, :, 2] += grid[:, :, FOOD] * 35

    # 4. Final step: Clip values to 0-255 and convert to 8-bit integers
    final_rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    # 5. Push to the surface
    # Note: surfarray uses (X, Y), so if your grid is (Y, X), use np.transpose
    pygame.surfarray.blit_array(surface, final_rgb)