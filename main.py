import random
import pygame
import json
import numpy as np
from entities import Ant, diffuse_pheromones, draw_grid, evap_rates, diffuse_rates
from ui import draw_custom_slider, draw, grow_food_clumps, draw_visibility_menu

pygame.init()

FOOD = 0
P_HOME = 1
P_FOOD = 2
P_FORAGER = 3
P_SCOUT = 4
ANT = 5

ui_alphas = [0.0, 0.0, 0.0, 0.0] 

# --- Window / grid setup ---

info = pygame.display.Info()

screen_width = min(info.current_w, info.current_h) - 50
screen_height = screen_width
width = 500
height = 500
def __main__():
    grid = np.zeros((width, height, 6), dtype=float)

    # Adding food
    grow_food_clumps(grid, num_clumps=width*height//5000, steps=5, spread_chance=0.3, width = width, height = height)

    # Automatically calculate tile size so the grid fits the window
    tile_size = screen_width // width

    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Ant Colony Grid")

    ant_num = 200

    # --- Define grid ---
                                        
    colony_pos = (width // 2, height // 2)
    ants = [Ant(colony_pos, 10) for _ in range(ant_num)]

    # Set the initial home scent at the center

    for ant in ants:
        grid[ant.x, ant.y, ANT] += ant.health/500


    draw_type = FOOD

    # --- Main loop ---
    clock = pygame.time.Clock()
    # This small surface corresponds to our 75x75 grid
    grid_surface = pygame.Surface((width, height))
    running = True

    show_menu = False
    visibility = {
        "P_HOME": True,
        "P_FOOD": True,
        "P_SCOUT": True,
        "P_FORAGER": True,
        "FOOD": True,
        "ANTS": True
    }
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

        keys = pygame.key.get_pressed()
        show_menu = keys[pygame.K_v]

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                brush_size = max(1, brush_size + event.y)
            elif event.type == pygame.KEYDOWN:
                if event.unicode in ['1', '2', '3', '4', '5', '6']:
                    draw_type = int(event.unicode) - 1
                elif event.key == pygame.K_r:
                    __main__()  # Restart the simulation
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the V key is currently being held down
                if pygame.key.get_pressed()[pygame.K_v]:
                    mx, my = pygame.mouse.get_pos()
                    center_x, center_y = screen_width // 2, screen_height // 2
                    
                    # This loop must match the order in your visibility dictionary
                    for i, key in enumerate(visibility.keys()):
                        # This Rect needs to match the one in ui.py exactly
                        button_rect = pygame.Rect(center_x - 80, center_y - 100 + i * 40, 160, 30)
                        if button_rect.collidepoint(mx, my):
                            visibility[key] = not visibility[key]

                    

        # Mouse
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]: # 0 is Left Click
            mx, my = pygame.mouse.get_pos()
            if not (mx < 200 and my < 150): 
                draw(grid, screen_width, screen_height, draw_type, brush_size, 16)
        if mouse_buttons[2]:
            mx, my = pygame.mouse.get_pos()
            if not (mx < 200 and my < 150): 
                draw(grid, screen_width, screen_height, draw_type, brush_size, -10)

        grid[colony_pos[0], colony_pos[1], P_HOME] = 256.0
        diffuse_pheromones(grid, width, height)

        grid[:, :, 2:5] = np.clip(grid[:, :, 2:5], 0, 128)

        draw_grid(grid_surface, grid, visibility)

        scaled_surface = pygame.transform.scale(grid_surface, (screen_width, screen_height))
        screen.blit(scaled_surface, (0, 0))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_v]:
            draw_visibility_menu(screen, visibility)
        
        labels = ["Home Decay", "Food Decay", "Forager Decay", "Scout Decay"]
        for i in range(4):
            # Expanded range (0.9 to 1.0) for better control
            evap_rates[i] = draw_custom_slider(screen, 20, 10 + i * 35, 150, evap_rates[i], 0.9, 1.0, labels[i])

        cursor_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        mx, my = pygame.mouse.get_pos()

        # Draw a soft circle (mapping grid brush_size back to screen pixels)
        screen_brush_radius = int(brush_size * (screen_width / width))
        pygame.draw.circle(cursor_surf, (255, 255, 255, 50), (mx, my), screen_brush_radius)
        pygame.draw.circle(cursor_surf, (255, 255, 255, 100), (mx, my), screen_brush_radius, 2)

        screen.blit(cursor_surf, (0, 0))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    __main__()
