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

ant_num = 50
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

        self.x = max(0, min(width - 1, self.x))
        self.y = max(0, min(height - 1, self.y))

# --- Define grid ---

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

    clock.tick(25)

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
    grid[colony_pos[1]] [colony_pos[0]].pheromones['home'] = 64

    current_pheromones = [[grid[y][x].pheromones["home"] for x in range(width)] for y in range(height)]

    for y in range(height):
        for x in range(width):

            neighbor_pheromone = 0
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < width and 0 <= ny < height:
                     neighbor_pheromone += current_pheromones[ny][nx]
                
            diffusion_factor = 0.25
            evaporation = 0.999
            
            current_scent = current_pheromones[y][x]
            new_scent = (current_scent * (1 - 4 * diffusion_factor)) + (neighbor_pheromone * diffusion_factor)
            grid[y][x].pheromones["home"] = new_scent * evaporation


    for y in range(height):
        for x in range(width):
            if grid[y][x].pheromones["home"] > 6 or grid[y][x].ant != 0:
                red = min(255, grid[y][x].ant * 75)
                green = min(255, int(grid[y][x].pheromones["home"] * 4)) 
                colour = (red, green, 0)
            else:
                colour = (10, 10, 10)
            pygame.draw.rect(screen, colour, (x * tile_size, y * tile_size, tile_size, tile_size))

    # --- Update display ---
    pygame.display.flip()

pygame.quit()