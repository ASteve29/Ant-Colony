import random
import pygame
import numpy as np
from entities import Ant, diffuse_pheromones, draw_grid

pygame.init()

FOOD = 0
ANT = 1
P_HOME = 2
P_FOOD = 3
P_FORAGER = 4
P_SCOUT = 5

# --- Window / grid setup ---


info = pygame.display.Info()

screen_width = min(info.current_w, info.current_h) - 50
screen_height = screen_width
width = 500
height = 500

grid = np.zeros((width, height, 6), dtype=float)

food_vals = [0, 1, 2, 4, 8, 16]
food_weights = [50000, 25, 12, 6, 3, 1]
probs = np.array(food_weights) / sum(food_weights)

grid[:, :, FOOD] = np.random.choice(food_vals, size=(width, height), p=probs)

# Automatically calculate tile size so the grid fits the window
tile_size = screen_width // width

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Ant Colony Grid")

ant_num = 200

# --- Define grid ---
		                        	
colony_pos = (width // 2, height // 2)
ants = [Ant(colony_pos, 30) for _ in range(ant_num)]

# Set the initial home scent at the center

for ant in ants:
    grid[ant.x, ant.y, ANT] += ant.health/500



# --- Main loop ---
clock = pygame.time.Clock()
# This small surface corresponds to our 75x75 grid
grid_surface = pygame.Surface((width, height))
running = True



while running:

    clock.tick(25)
    
    grid[ :, :, ANT] = 0
    if random.randrange(0, 100, 1) > 90:
        ants.append(Ant(colony_pos, 5))
    ants = [ant for ant in ants if ant.health > 0]
    for ant in ants:
        ant.move(grid, width, height)
        grid[ant.x, ant.y, ANT] += ant.health/1000


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0]: # 0 is Left Click
        mx, my = pygame.mouse.get_pos()
        grid_x = int(mx * (width / screen_width))
        grid_y = int(my * (height / screen_height))
        
        if 0 <= grid_x < width and 0 <= grid_y < height:
            # Paint a small 3x3 square of food
            grid[grid_x-1:grid_x+2, grid_y-1:grid_y+2, FOOD] += 1

    grid[colony_pos[0], colony_pos[1], P_HOME] = 128.0
    diffuse_pheromones(grid, width, height)

    draw_grid(grid_surface, grid)

    scaled_surface = pygame.transform.scale(grid_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()

pygame.quit()