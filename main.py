import random
import pygame

pygame.init()

# --- Window / grid setup ---
screen_width = 500
screen_height = 500
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
        self.ant = 0
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
    def move(self):
        self.x = self.x + random.randint(-1, 1)
        self.y = self.y + random.randint(-1, 1)

grid = [[Tile() for x in range(width)] for y in range(height)]

colony_pos = (width // 2, height // 2)
ants = [Ant(colony_pos) for _ in range(ant_num)]
grid[colony_pos[1]] [colony_pos[0]].pheromones['home'] = 64

for ant in ants:
    grid[ant.y] [ant.x].ant += 1

clock = pygame.time.Clock()

# --- Main loop ---
running = True
while running:

    clock.tick(1)

    for y in range(height):
        for x in range(width):
            grid[y][x].ant = 0
    
    for ant in ants:
        ant.move()
        grid[ant.y] [ant.x].ant += 1

    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Clear screen ---
    screen.fill((0, 0, 0))

    # --- Draw grid ---
    for y in range(height):
        for x in range(width):
            if grid[y][x].pheromones["home"] > 0 or grid[y][x].ant != 0:
                colour = (grid[y][x].ant * 50, grid[y][x].pheromones["home"]*1.5, 0)  # home pheromone tile green
            else:
                colour = (50, 50, 50)  # Empty tile grey
            pygame.draw.rect(screen, colour, (x * tile_size, y * tile_size, tile_size, tile_size))

    # --- Update display ---
    pygame.display.flip()

pygame.quit()