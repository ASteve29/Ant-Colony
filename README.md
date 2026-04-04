# Ant Colony Simulation

A simulation of ants that use pheromones to explore and navigate a grid.

## What it does

- Ants move around a grid
- They leave pheromone trails
- Trails diffuse and evaporate over time
- Ants make decisions based on these signals

## How it works

### Grid
The world is represented as a 2D grid of tiles with the "home" at the centre and food places randomly.

### Ants
Each ant has a position, goal, and simple behaviour rules and can leave pheromones.

### Pheromones
Multiple pheromone types exist (home, food, etc.), each with:
- diffusion
- evaporation

### Behaviour
Ants choose movement based on weighted pheromone signals.

## Features

- Multiple pheromone system
- Configurable diffusion and evaporation
- Goal-based decision making
- Visual simulation using pygame

## How to run

Install pygame and run:
```bash
pip install pygame
python main.py
```
