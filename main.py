import random
import pygame
from entities import Ant,Tile, diffuse_pheremones

pygame.init()

# Window / grid setup
screen_width = 500
screen_height = 500
width = 75
height = 75

# Automatically calculate tile size so the grid fits the window
tile_size = screen_width // width

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Ant Colony Grid")

ant_num = 50
jobs = ["scout", "forager"]
goals = ["find food", "go home", "explore", "mate"]


# Define grid

grid = [[Tile() for x in range(width)] for y in range(height)]

colony_pos = (width // 2, height // 2)
ants = [Ant(colony_pos) for _ in range(ant_num)]
grid[colony_pos[1]] [colony_pos[0]].pheromones['home'] = 64

for ant in ants:
    grid[ant.y] [ant.x].ant += 1


# Main loop

clock = pygame.time.Clock()
grid_surface = pygame.Surface((width, height))
running = True
while running:

    clock.tick(25)

    for y in range(height):
        for x in range(width):
            grid[y][x].ant = 0
    
    ants = [ant for ant in ants if ant.health > 0]

    for ant in ants:
        ant.move(width, height)
        grid[ant.y] [ant.x].ant += 1

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False



    # Clear screen
    screen.fill((0, 0, 0))

    grid[colony_pos[1]][colony_pos[0]].pheromones['home'] = 64
    diffuse_pheremones(grid, width, height)

    grid_surface.fill((0, 0, 0))

    # Open the PixelArray to "lock" the surface for fast editing
    pixels = pygame.PixelArray(grid_surface)
    
    for y in range(height):
        for x in range(width):
            tile = grid[y][x]
            # Use your existing color logic
            if tile.pheromones["home"] > 0 or tile.ant != 0:
                red = min(255, tile.ant * 75)
                green = min(255, int(tile.pheromones["home"] * 4))
                # Set a single pixel instead of drawing a big rectangle
                pixels[x, y] = (red, green, 0)
    
    # IMPORTANT: Delete the PixelArray to "unlock" the surface before scaling
    del pixels

    # Scale the tiny 50x50 surface up to the 500x500 screen
    scaled_surface = pygame.transform.scale(grid_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (0, 0))

    # Update display
    pygame.display.flip()

pygame.quit()