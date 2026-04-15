import random
import pygame
import numpy as np
from entities import Ant, diffuse_pheromones, draw_grid, evap_rates, diffuse_rates
from ui import draw_custom_slider, draw, grow_food_clumps

pygame.init()

FOOD = 0
ANT = 1
P_HOME = 2
P_FOOD = 3
P_FORAGER = 4
P_SCOUT = 5

ui_alphas = [0.0, 0.0, 0.0, 0.0] 

# --- Window / grid setup ---

info = pygame.display.Info()

screen_width = min(info.current_w, info.current_h) - 50
screen_height = screen_width
width = 500
height = 500

grid = np.zeros((width, height, 6), dtype=float)

# Adding food
grow_food_clumps(grid, num_clumps=20, steps=5, spread_chance=0.3, width = width, height = height)

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

brush_size = 5
brush_layer = 0

while running:

    time_delta = clock.tick(25) / 1000.0 

    grid[ :, :, ANT] = 0
    if random.randrange(0, 100, 1) > 90:
        ants.append(Ant(colony_pos, 5))
    ants = [ant for ant in ants if ant.health > 0]
    for ant in ants:
        ant.move(grid, width, height)
        grid[ant.x, ant.y, ANT] += ant.health/1000

    # Event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            brush_size = max(1, brush_size + event.y)

    # Mouse
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0]: # 0 is Left Click
        mx, my = pygame.mouse.get_pos()
        if not (mx < 200 and my < 150): 
            draw(grid, screen_width, screen_height, FOOD, brush_size, 1)
    if mouse_buttons[2]:
        mx, my = pygame.mouse.get_pos()
        if not (mx < 200 and my < 150): 
            draw(grid, screen_width, screen_height, FOOD, brush_size, -10)

    grid[colony_pos[0], colony_pos[1], P_HOME] = 128.0
    diffuse_pheromones(grid, width, height)

    draw_grid(grid_surface, grid)

    scaled_surface = pygame.transform.scale(grid_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (0, 0))

    for i in range(4):
        evap_rates[i] = draw_custom_slider(screen, 20, 10 + i * 35, 150, evap_rates[i], 0.99, 1, "Home Evap")

    cursor_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    mx, my = pygame.mouse.get_pos()

    # Draw a soft circle (mapping grid brush_size back to screen pixels)
    screen_brush_radius = int(brush_size * (screen_width / width))
    pygame.draw.circle(cursor_surf, (255, 255, 255, 50), (mx, my), screen_brush_radius)
    pygame.draw.circle(cursor_surf, (255, 255, 255, 100), (mx, my), screen_brush_radius, 2)

    screen.blit(cursor_surf, (0, 0))

    pygame.display.flip()

pygame.quit()