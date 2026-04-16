import pygame
import numpy as np
import random

FOOD = 0
P_HOME = 1
P_FOOD = 2
P_FORAGER = 3
P_SCOUT = 4
ANT = 5

def draw(grid, screen_width, screen_height, layer_index, size, intensity):
    mx, my = pygame.mouse.get_pos()

    gx = int(mx * (grid.shape[0] / screen_width))
    gy = int(my * (grid.shape[1] / screen_height))

    y, x = np.ogrid[-size:size+1, -size:size+1]
    mask = np.exp(-(x**2 + y**2) / (2 * (size/2)**2))
    
    # Define bounds (ensure we stay inside the array)
    x1, x2 = max(0, gx-size), min(grid.shape[0], gx+size+1)
    y1, y2 = max(0, gy-size), min(grid.shape[1], gy+size+1)
    
    # Adjust the mask if it's hitting the edges of the screen
    m_x1 = size - (gx - x1)
    m_x2 = m_x1 + (x2 - x1)
    m_y1 = size - (gy - y1)
    m_y2 = m_y1 + (y2 - y1)
    
    if layer_index == FOOD and intensity > 0:
        # CLUMP MODE
        for _ in range(10): # 10 small clumps per click
            # Pick a random spot inside the brush radius
            offset_x = random.randint(-size, size)
            offset_y = random.randint(-size, size)

            if offset_x**2 + offset_y**2 >= size**2 - 1:
                continue
            
            # Place a small, sharp "grain" of food
            ix, iy = gx + offset_x, gy + offset_y
            
            if 0 <= ix < grid.shape[0] and 0 <= iy < grid.shape[1]:
                grid[ix, iy, FOOD] += intensity * 5 
    else:
        # Add the "soft" intensity to the grid
        grid[x1:x2, y1:y2, layer_index] += mask[m_x1:m_x2, m_y1:m_y2] * intensity
    
    # Clip it to 0
    grid[x1:x2, y1:y2, layer_index] = np.clip(grid[x1:x2, y1:y2, layer_index], 0, 100)

def draw_custom_slider(screen, x, y, width, value, val_min, val_max, label):
    # 1. Check for Hover
    mouse_pos = pygame.mouse.get_pos()
    # Define the 'hitbox' for the whole slider row
    slider_rect = pygame.Rect(x, y, width + 20, 30)
    
    is_hovering = slider_rect.collidepoint(mouse_pos)
    
    # Set dynamic alpha based on hover
    track_alpha = 80 if is_hovering else 30
    knob_alpha = 200 if is_hovering else 60
    
    # 2. Create Surface
    ui_surf = pygame.Surface((width + 20, 40), pygame.SRCALPHA)
    
    # 3. Draw Track
    pygame.draw.rect(ui_surf, (150, 150, 150, track_alpha), (10, 18, width, 4), border_radius=2)

    # 4. Math for Knob (using the val_min/val_max fix)
    visual_ratio = (value - val_min) / (val_max - val_min) if val_max != val_min else 0
    knob_x = 10 + (np.clip(visual_ratio, 0, 1) * width)
    
    # 5. Draw Knob
    pygame.draw.circle(ui_surf, (0, 255, 255, knob_alpha), (int(knob_x), 20), 8)

    # 6. Blit and Handle Input
    screen.blit(ui_surf, (x - 10, y))

    if pygame.mouse.get_pressed()[0] and is_hovering:
        new_ratio = (mouse_pos[0] - x) / width
        return val_min + (np.clip(new_ratio, 0, 1) * (val_max - val_min))
            
    return value

def grow_food_clumps(grid, num_clumps=10, steps=15, spread_chance=0.3, width=500, height=500, FOOD=0):
    for _ in range(num_clumps):
        cx, cy = np.random.randint(100, width-100), np.random.randint(100, height-100)
        grid[cx, cy, FOOD] = 16

    for _ in range(steps):
        food_mask = grid[:, :, FOOD] > 0
        
        # 8-way neighbors (Up, Down, Left, Right + Diagonals)
        neighbors = np.zeros_like(food_mask)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                neighbors |= np.roll(np.roll(food_mask, dx, axis=0), dy, axis=1)

        # Potential new growth areas
        growth_candidates = neighbors & ~food_mask
        
        # KEY: Only grow if a random roll is less than spread_chance
        # This breaks the "perfect diamond" symmetry
        random_roll = np.random.rand(width, height) < spread_chance
        actual_growth = growth_candidates & random_roll

        num_new_tiles = np.count_nonzero(actual_growth)
        if num_new_tiles > 0:
            # Vary the food density (1, 2, 4, 8)
            vals = [1, 2, 4, 8]
            probs = [0.8, 0.15, 0.04, 0.01] # Weighted towards lower density
            grid[actual_growth, FOOD] = np.random.choice(vals, size=num_new_tiles, p=probs)