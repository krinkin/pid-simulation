import pygame
import numpy as np
from typing import Tuple


class Platform:
    def __init__(self, x: float, y: float, mass: float = 1.0):
        self.x = x
        self.y = y
        self.mass = mass
        self.velocity = 0.0
        self.acceleration = 0.0
        
        # Visual properties
        self.width = 100
        self.height = 20
        self.color = (100, 100, 200)
        
        # Physics parameters
        self.friction_coefficient = 0.1
        
    def apply_force(self, force: float):
        """Apply horizontal force to the platform"""
        self.acceleration = force / self.mass
        
    def update(self, dt: float):
        """Update platform physics"""
        # Apply friction
        friction_force = -self.friction_coefficient * self.velocity
        friction_acceleration = friction_force / self.mass
        
        # Update velocity and position
        self.velocity += (self.acceleration + friction_acceleration) * dt
        self.x += self.velocity * dt
        
        # Reset acceleration for next frame
        self.acceleration = 0.0
        
    def set_position(self, x: float):
        """Instantly set platform position (for click handling)"""
        self.x = x
        self.velocity = 0.0
        self.acceleration = 0.0
        
    def draw(self, screen: pygame.Surface):
        """Draw the platform"""
        rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (50, 50, 100), rect, 2)  # Border
        
    def get_position(self) -> float:
        """Get current x position"""
        return self.x