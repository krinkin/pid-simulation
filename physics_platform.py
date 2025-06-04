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
        self.wind_force = 0.0
        
    def apply_force(self, force: float):
        """Apply horizontal force to the platform"""
        self.acceleration = force / self.mass
        
    def update(self, dt: float):
        """Update platform physics"""
        # Store the control force before modifications
        control_force = self.acceleration * self.mass
        
        # Apply wind as a constant external force
        wind_acceleration = self.wind_force / self.mass
        
        # Apply velocity-dependent damping
        damping = 0.1
        damping_acceleration = -damping * self.velocity
        
        # Calculate total force including wind
        total_force = control_force + self.wind_force
        
        # Apply deadband - if total force is too small, platform doesn't move
        deadband_threshold = 5.0
        
        if abs(total_force) < deadband_threshold:
            # In deadband - high static friction prevents movement
            if abs(self.velocity) < 0.5:
                # Stop completely if moving slowly
                self.velocity = 0
                self.acceleration = 0
                return
            else:
                # Apply heavy damping if still moving
                damping_acceleration = -0.5 * self.velocity
        
        # Update velocity and position
        total_acceleration = self.acceleration + wind_acceleration + damping_acceleration
        self.velocity += total_acceleration * dt
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