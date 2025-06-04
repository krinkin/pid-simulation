import pygame
import numpy as np
from dataclasses import dataclass
from typing import Tuple
from platform import Platform


@dataclass
class SimulationConfig:
    width: int = 1200
    height: int = 800
    fps: int = 60
    background_color: Tuple[int, int, int] = (240, 240, 240)
    center_line_color: Tuple[int, int, int] = (200, 200, 200)
    
    # Physics
    gravity: float = 9.81
    friction: float = 0.1


class PIDSimulator:
    def __init__(self, config: SimulationConfig = SimulationConfig()):
        self.config = config
        pygame.init()
        self.screen = pygame.display.set_mode((config.width, config.height))
        pygame.display.set_caption("PID Controller Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 1.0 / config.fps
        
        # Center position
        self.center_x = config.width // 2
        
        # Create platform at center
        self.platform = Platform(
            x=self.center_x,
            y=config.height // 2,
            mass=1.0
        )
        
    def draw(self):
        self.screen.fill(self.config.background_color)
        
        # Draw center line
        pygame.draw.line(
            self.screen, 
            self.config.center_line_color,
            (self.center_x, 0),
            (self.center_x, self.config.height),
            2
        )
        
        # Draw platform
        self.platform.draw(self.screen)
        
        pygame.display.flip()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle click - platform will be moved here
                mouse_x, _ = pygame.mouse.get_pos()
                self.platform.set_position(mouse_x)
                
    def run(self):
        while self.running:
            self.handle_events()
            self.platform.update(self.dt)
            self.draw()
            self.clock.tick(self.config.fps)
        
        pygame.quit()


if __name__ == "__main__":
    simulator = PIDSimulator()
    simulator.run()