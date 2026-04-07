import random
import pygame
# This pulls in everything you built in your other file!
from entities import Ant, Tile, diffuse_pheromones, draw_grid

pygame.init()

# --- Window / grid setup ---

info = pygame.display.Info()

screen_width = min(info.current_w, info.current_h)
screen_height = screen_width
width = 200
height = 200

# Automatically calculate tile size so the grid fits the window
tile_size = screen_width // width

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Ant Colony Grid")

ant_num = 200

# --- Define grid ---
grid = [[Tile() for x in range(width)] for y in range(height)]
for y in range(height):
	for x in range(width):
		if grid[y][x].food > 0:
			for dy in [-1, 0, 1]:
				for dx in [-1, 0, 1]:
					ny, nx = dy+y, dx+x
					if ny < height and nx < width:
						grid[ny][nx].food += random.choices([0, 1, 2, 4, 8, 16], weights = [200, 25, 12, 6, 3, 1], k=1)[0]
		                        	
colony_pos = (width // 2, height // 2)
ants = [Ant(colony_pos) for _ in range(ant_num)]

# Set the initial home scent at the center
grid[colony_pos[1]][colony_pos[0]].pheromones['home'] = 64.0

for ant in ants:
    grid[ant.y][ant.x].ant += ant.health/1000




# --- Main loop ---
clock = pygame.time.Clock()
# This small surface corresponds to our 75x75 grid
grid_surface = pygame.Surface((width, height))
running = True



while running:

    clock.tick(50)
    
    for y in range(height):
        for x in range(width):
            grid[y][x].ant = 0


    ants = [ant for ant in ants if ant.health > 0]


    for ant in ants:
        ant.move(grid, width, height)
        grid[ant.y][ant.x].ant += ant.health/1000


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    grid[colony_pos[1]][colony_pos[0]].pheromones['home'] = 64.0
    diffuse_pheromones(grid, width, height)

    draw_grid(grid_surface, grid, width, height)

    scaled_surface = pygame.transform.scale(grid_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()

pygame.quit()