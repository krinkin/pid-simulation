import pygame
import numpy as np
from dataclasses import dataclass
from typing import Tuple
from platform import Platform
from pid_controller import PIDController
from ui_controls import ControlPanel


@dataclass
class SimulationConfig:
    width: int = 1200
    height: int = 800
    fps: int = 60
    background_color: Tuple[int, int, int] = (240, 240, 240)
    center_line_color: Tuple[int, int, int] = (200, 200, 200)
    control_panel_width: int = 400
    
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
        
        # Simulation area (excluding control panel)
        self.sim_width = config.width - config.control_panel_width
        self.center_x = self.sim_width // 2
        
        # Create platform at center of simulation area
        self.platform = Platform(
            x=self.center_x,
            y=config.height // 2,
            mass=1.0
        )
        
        # Create PID controller
        self.pid = PIDController(kp=2.0, ki=0.1, kd=0.5)
        
        # Create control panel on the right side
        self.control_panel = ControlPanel(self.sim_width + 20, 20)
        
        # PID enabled states
        self.pid_enabled = {'kp': True, 'ki': True, 'kd': True}
        
        # Fonts for display
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
    def draw(self):
        self.screen.fill(self.config.background_color)
        
        # Draw vertical separator
        pygame.draw.line(
            self.screen,
            (150, 150, 150),
            (self.sim_width, 0),
            (self.sim_width, self.config.height),
            2
        )
        
        # Draw center line in simulation area
        pygame.draw.line(
            self.screen, 
            self.config.center_line_color,
            (self.center_x, 0),
            (self.center_x, self.config.height),
            2
        )
        
        # Draw platform
        self.platform.draw(self.screen)
        
        # Draw force visualization
        if hasattr(self.pid, 'state') and self.pid.state.output != 0:
            self.draw_force_arrow()
        
        # Draw control panel
        self.control_panel.draw(self.screen)
        
        # Draw PID state info
        self.draw_pid_info()
        
        # Draw component bars
        self.draw_component_bars()
        
        pygame.display.flip()
        
    def draw_force_arrow(self):
        """Draw force arrow on platform"""
        force_scale = 2.0
        force_x = int(self.pid.state.output * force_scale)
        
        # Draw force arrow
        arrow_y = self.platform.y
        arrow_start = (self.platform.x, arrow_y)
        arrow_end = (self.platform.x + force_x, arrow_y)
        
        pygame.draw.line(self.screen, (255, 0, 0), arrow_start, arrow_end, 3)
        
        # Arrow head
        if force_x != 0:
            sign = 1 if force_x > 0 else -1
            pygame.draw.polygon(self.screen, (255, 0, 0), [
                arrow_end,
                (arrow_end[0] - sign * 10, arrow_end[1] - 5),
                (arrow_end[0] - sign * 10, arrow_end[1] + 5)
            ])
            
    def draw_pid_info(self):
        """Draw PID state information"""
        if not hasattr(self.pid, 'state'):
            return
            
        x_offset = self.sim_width + 20
        y_offset = 250
        
        # Title
        title = self.font.render("PID State", True, (0, 0, 0))
        self.screen.blit(title, (x_offset, y_offset))
        
        y_offset += 35
        
        # Error
        error_text = self.small_font.render(
            f"Error: {self.pid.state.error:.2f}", 
            True, (0, 0, 0)
        )
        self.screen.blit(error_text, (x_offset, y_offset))
        
        y_offset += 25
        
        # Get components
        p_term, i_term, d_term = self.pid.get_components()
        
        # Apply enabled states
        if not self.pid_enabled.get('kp', True):
            p_term = 0
        if not self.pid_enabled.get('ki', True):
            i_term = 0
        if not self.pid_enabled.get('kd', True):
            d_term = 0
        
        # P component
        p_text = self.small_font.render(
            f"P component: {p_term:.2f}", 
            True, (0, 100, 0)
        )
        self.screen.blit(p_text, (x_offset, y_offset))
        
        y_offset += 25
        
        # I component
        i_text = self.small_font.render(
            f"I component: {i_term:.2f}", 
            True, (100, 0, 0)
        )
        self.screen.blit(i_text, (x_offset, y_offset))
        
        y_offset += 25
        
        # D component
        d_text = self.small_font.render(
            f"D component: {d_term:.2f}", 
            True, (0, 0, 100)
        )
        self.screen.blit(d_text, (x_offset, y_offset))
        
        y_offset += 25
        
        # Total output
        output_text = self.small_font.render(
            f"Total output: {self.pid.state.output:.2f}", 
            True, (0, 0, 0)
        )
        self.screen.blit(output_text, (x_offset, y_offset))
        
    def draw_component_bars(self):
        """Draw visual bars for PID components"""
        if not hasattr(self.pid, 'state'):
            return
            
        bar_x = self.sim_width + 20
        bar_y = 450
        bar_width = 360
        bar_height = 20
        max_value = 50  # Scale for visualization
        
        # Get components
        p_term, i_term, d_term = self.pid.get_components()
        
        # Apply enabled states
        if not self.pid_enabled.get('kp', True):
            p_term = 0
        if not self.pid_enabled.get('ki', True):
            i_term = 0
        if not self.pid_enabled.get('kd', True):
            d_term = 0
        
        # P bar
        self.draw_bar(bar_x, bar_y, bar_width, bar_height, 
                     p_term, max_value, (0, 150, 0), "P")
        
        # I bar
        bar_y += 30
        self.draw_bar(bar_x, bar_y, bar_width, bar_height,
                     i_term, max_value, (150, 0, 0), "I")
        
        # D bar
        bar_y += 30
        self.draw_bar(bar_x, bar_y, bar_width, bar_height,
                     d_term, max_value, (0, 0, 150), "D")
        
    def draw_bar(self, x, y, width, height, value, max_value, color, label):
        """Draw a single component bar"""
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (200, 200, 200), bg_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), bg_rect, 1)
        
        # Center line
        center_x = x + width // 2
        pygame.draw.line(self.screen, (150, 150, 150),
                        (center_x, y), (center_x, y + height), 2)
        
        # Value bar
        normalized_value = max(-1, min(1, value / max_value))
        bar_width_pixels = int(abs(normalized_value) * (width // 2))
        
        if normalized_value > 0:
            bar_rect = pygame.Rect(center_x, y, bar_width_pixels, height)
        else:
            bar_rect = pygame.Rect(center_x - bar_width_pixels, y, bar_width_pixels, height)
            
        pygame.draw.rect(self.screen, color, bar_rect)
        
        # Label
        label_text = self.small_font.render(label, True, (0, 0, 0))
        self.screen.blit(label_text, (x - 20, y))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Only handle clicks in simulation area
                mouse_x, _ = pygame.mouse.get_pos()
                if mouse_x < self.sim_width:
                    self.platform.set_position(mouse_x)
                
            # Handle control panel events
            changed = self.control_panel.handle_event(event)
            if changed:
                # Update PID gains
                if 'kp' in changed:
                    self.pid.kp = changed['kp']
                if 'ki' in changed:
                    self.pid.ki = changed['ki']
                if 'kd' in changed:
                    self.pid.kd = changed['kd']
                # Update platform mass
                if 'mass' in changed:
                    self.platform.mass = changed['mass']
                # Update enabled states
                if 'kp_enabled' in changed:
                    self.pid_enabled['kp'] = changed['kp_enabled']
                if 'ki_enabled' in changed:
                    self.pid_enabled['ki'] = changed['ki_enabled']
                if 'kd_enabled' in changed:
                    self.pid_enabled['kd'] = changed['kd_enabled']
                
    def run(self):
        while self.running:
            self.handle_events()
            
            # PID control
            force = self.pid.update(
                setpoint=self.center_x,
                current_value=self.platform.get_position(),
                dt=self.dt,
                enabled=self.pid_enabled
            )
            self.platform.apply_force(force)
            
            self.platform.update(self.dt)
            self.draw()
            self.clock.tick(self.config.fps)
        
        pygame.quit()


if __name__ == "__main__":
    simulator = PIDSimulator()
    simulator.run()