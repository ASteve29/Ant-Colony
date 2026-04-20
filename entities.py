import random
import pygame
import json
import numpy as np
from scipy.ndimage import convolve

with open('config.json', 'r') as f:
    CONFIG = json.load(f)

FOOD = 0
P_HOME = 1
P_FOOD = 2
P_FORAGER = 3
P_SCOUT = 4
ANT = 5

P_MAP = {
    "home": P_HOME,
    "food": P_FOOD,
    "forager ant": P_FORAGER,
    "scout ant": P_SCOUT
}

baseline_amount = CONFIG['pheromones']['baseline_amount']
jobs = [P_SCOUT, P_FORAGER]
goals = ["find food", "go home", "explore", "mate"]

evap_rates = CONFIG['pheromones']['evap_rates'].copy()
diffuse_rates = CONFIG['pheromones']['diffuse_rates'].copy()

goal_targets = CONFIG['ants_behavior']['goal_targets']

goal_targets = {
    "find food": {"home": -50, "food": 10, "forager ant": 10, "scout ant": 0.1},
    "go home": {"home": 50, "food": 0.01, "forager ant": 0.1, "scout ant": 0.1},
    "explore": {"home": -50, "food": 5, "forager ant": 0.1, "scout ant": 0.1},
    "mate": {"home": 0.5, "food": 0.1, "forager ant": 1, "scout ant": 1}
}

# Classes

class Ant:
    def __init__(self, pos, spawn_range):
        self.x = pos[0] + random.randint(-spawn_range, spawn_range)
        self.y = pos[1] + random.randint(-spawn_range, spawn_range)
        self.dx = 0
        self.dy = 0
        self.old_x = 0
        self.old_y = 0
        self.job = P_SCOUT
        self.goal = "explore"
        self.health = 1000
        self.food = 0
        self.trail_strength = 0

    def move(self, grid, width, height):
        self.old_x = self.x
        self.old_y = self.y

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
                    step_len = np.sqrt(dx**2 + dy**2)
                    normalized_dot = np.dot([dx/step_len, dy/step_len], [self.dx, self.dy])
                    total_score += val * target_weight + (normalized_dot * 2)
                weights.append(total_score)

        min_score = min(weights)
        weights = [w - min_score + 1 for w in weights]

        self.x, self.y = random.choices(options, weights=weights, k=1)[0]

        self.dx = self.x - self.old_x
        self.dy = self.y - self.old_y

        self.health -= 1

    def switch_job(self, grid, width, height):
        if self.job == P_SCOUT and grid[self.x, self.y, P_SCOUT] > 16:
            new_job = random.choices(jobs, weights=[100, grid[self.x, self.y, P_SCOUT]/8])[0]
            if new_job != self.job:
                self.job = new_job
                self.goal = "find food"

        if self.job == P_FORAGER and grid[self.x, self.y, P_FORAGER] > 16:
            new_job = random.choices(jobs, weights=[grid[self.x, self.y, P_FORAGER]/8, 100])[0]
            if new_job != self.job:
                self.job = new_job
                self.goal = "explore"

    def drop_pheromones(self, grid, width, height):
        if self.goal == "go home" and self.job == P_FORAGER:
            grid[self.x, self.y, P_FOOD] += min(128, (self.trail_strength / 10) * np.exp(self.health/500)) * 2
            self.trail_strength -= 1
            if grid[self.x, self.y, P_HOME] > 64 and self.food > 0:
                self.health += 50 * self.food
                self.food = 0
                self.goal = "find food"
                self.trail_strength += 50
        elif self.goal in ["find food", "explore"]:
            grid[self.x, self.y, P_HOME] += min(32, self.health/500 + (self.trail_strength / 50)) * 2
        
        # Job-specific scent
        scent_idx = P_FORAGER if self.job == P_FORAGER else P_SCOUT
        grid[self.x, self.y, scent_idx] += min(5, 5 * (self.health/500))

        if self.goal == "find food" and grid[self.x, self.y, FOOD] == 0:
            if grid[self.x, self.y, P_FOOD] > 0.1:
                grid[self.x, self.y, P_FOOD] *= 0.9

    def sense_food(self, grid, width, height):
        # 1. Food Sensing (Index 0)
        if grid[self.x, self.y, FOOD] > 0:
            self.food += 1
            self.health += 10
            self.job = P_FORAGER
            self.goal = "go home"
            self.trail_strength += 10 * self.food
            grid[self.x, self.y, FOOD] -= 1

    def update(self, grid, width, height):
        self.sense_food(grid, width, height)
        self.drop_pheromones(grid, width, height)
        self.switch_job(grid, width, height)
        self.move(grid, width, height)
        

# Functions
def diffuse_pheromones(grid, width, height): # High value = spreads faster

    for i in range(len(evap_rates)):
        rate = evap_rates[i]
        diff = diffuse_rates[i]
        
        if i == P_HOME:
            # Ensure the total sum of the kernel equals the evaporation rate
            center = rate - diff
            side = diff / 8
            
            kernel = np.array([
                [side, side, side],
                [side, center, side],
                [side, side, side]
            ])
            
            grid[:, :, i + 1] = convolve(grid[:, :, i + 1], kernel, mode='constant')
            continue

        # Apply to the correct layer (starting at index 2)
        grid[:, :, i + 1] *= rate

def draw_grid(surface, grid, visibility):
    # 1. Create an empty RGB array (Width x Height x 3)
    # Use float32 for calculations to avoid rounding errors during math
    rgb = np.zeros((grid.shape[0], grid.shape[1], 3), dtype=np.float32)

    # 2. Apply your colour_map logic using NumPy layers
    # Scout Ant Pheromone (Layer 5) -> (3, 0, 3)
    if visibility["P_SCOUT"]:
        scout_ant = grid[:, :, P_SCOUT]
        rgb[:, :, 0] += scout_ant * 3
        rgb[:, :, 2] += scout_ant * 3

    # Forager Ant Pheromone (Layer 4) -> (0, 3, 3)
    if visibility["P_FORAGER"]:
        forager_ant = grid[:, :, P_FORAGER]
        rgb[:, :, 1] += forager_ant * 3
        rgb[:, :, 2] += forager_ant * 3

    # Home Pheromone (Layer 2) -> (0, 2, 0)
    if visibility["P_HOME"]:
        home_ant = grid[:, :, P_HOME]
        rgb[:, :, 1] += home_ant

    # Food Pheromone (Layer 3) -> (2, 2, 0)
    if visibility["P_FOOD"]:
        food_p_ant = grid[:, :, P_FOOD]
        rgb[:, :, 0] += food_p_ant * 2
        rgb[:, :, 1] += food_p_ant * 2

    # 3. Add the actual Food and Ants (the "Physical" layers)
    # You used + tile.ant * 100 + tile.food * 10 in your original code
    if visibility["ANTS"]:
        rgb[:, :, 0] += grid[:, :, ANT] * 128
    
    if visibility["FOOD"]:
        rgb[:, :, 0] += grid[:, :, FOOD] * 75
        rgb[:, :, 1] += grid[:, :, FOOD] * 35

    # 4. Final step: Clip values to 0-255 and convert to 8-bit integers
    final_rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    # 5. Push to the surface
    pygame.surfarray.blit_array(surface, final_rgb)