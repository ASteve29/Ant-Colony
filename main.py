import random
import pygame

pygame.init()

# --- Window / grid setup ---
screen_width = 1100
screen_height = 1100
width = 50
height = 50

# Automatically calculate tile size so the grid fits the window
tile_size = screen_width // width

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ant Colony Grid")

ant_num = 5
jobs = ["scout", "forager"]
goals = ["find food", "to home"]

# --- Classes ---
class Tile:
    def __init__(self):
        self.food = 0
        self.ant = None
        self.pheromones = {
            "home": 0,
            "food": 0
        }

class Ant:
    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.job = "scout"
        self.goal = "find food"
    # def move(self):

# --- Grid and colony ---
grid = [[Tile() for x in range(width)] for y in range(height)]

colony_pos = (width // 2, height // 2)
grid[colony_pos[1]][colony_pos[0]].pheromones['home'] = 64

# --- Main loop ---
running = True
while running:
    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Clear screen ---
    screen.fill((0, 0, 0))

    # --- Draw grid ---
    for y in range(height):
        for x in range(width):
            if grid[y][x].pheromones["home"] > 0:
                color = (0, grid[y][x].pheromones["home"]*2, 0)  # home pheromone tile green
            else:
                color = (50, 50, 50)  # Empty tile grey
            pygame.draw.rect(screen, color, (x * tile_size, y * tile_size, tile_size, tile_size))

    # --- Update display ---
    pygame.display.flip()