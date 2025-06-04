import pygame
import numpy as np
import time
from dataclasses import dataclass
from typing import Tuple
from physics_platform import Platform
from pid_controller import PIDController
from ui_controls import ControlPanel
from graph_plotter import GraphPlotter


@dataclass
class SimulationConfig:
    width: int = 1600
    height: int = 950
    fps: int = 60
    background_color: Tuple[int, int, int] = (240, 240, 240)
    center_line_color: Tuple[int, int, int] = (200, 200, 200)
    control_panel_width: int = 450  # Increased width for better layout
    graph_height: int = 400
    
    # Physics
    gravity: float = 9.81
    friction: float = 0.1
    
    # Simulation
    simulation_speed: float = 2.2  # 1.0 = real-time, 0.5 = half speed, 2.0 = double speed


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
        self.sim_height = config.height - config.graph_height
        self.center_x = self.sim_width // 2
        
        # Create platform at center of simulation area
        self.platform = Platform(
            x=self.center_x,
            y=self.sim_height // 2,
            mass=1.0
        )
        
        # Create PID controller
        self.pid = PIDController(kp=5.0, ki=0.5, kd=2.0)
        
        # Create control panel on the right side
        self.control_panel = ControlPanel(self.sim_width + 20, 20)
        
        # Create graph plotter at the bottom
        self.graph_plotter = GraphPlotter(
            x=10,
            y=self.sim_height + 10,
            width=self.sim_width - 20,
            height=config.graph_height - 20,
            time_window=20.0  # Show 20 seconds of data
        )
        
        # PID enabled states
        self.pid_enabled = {'kp': True, 'ki': True, 'kd': True}
        
        # Fonts for display
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 28)
        
        # Time tracking
        self.start_time = time.time()
        self.simulation_time = 0.0
        self.last_graph_update = 0
        self.graph_update_interval = 0.05  # Update graphs every 50ms
        
        # Simulation speed
        self.simulation_speed = config.simulation_speed
        
    def draw(self):
        self.screen.fill(self.config.background_color)
        
        # Draw boundaries
        # Vertical separator for control panel
        pygame.draw.line(
            self.screen,
            (150, 150, 150),
            (self.sim_width, 0),
            (self.sim_width, self.config.height),
            2
        )
        
        # Horizontal separator for graphs
        pygame.draw.line(
            self.screen,
            (150, 150, 150),
            (0, self.sim_height),
            (self.sim_width, self.sim_height),
            2
        )
        
        # Draw center line in simulation area
        pygame.draw.line(
            self.screen, 
            self.config.center_line_color,
            (self.center_x, 0),
            (self.center_x, self.sim_height),
            2
        )
        
        # Draw platform
        self.platform.draw(self.screen)
        
        # Draw wind indicator
        self.draw_wind_indicator()
        
        # Draw deadband indicator
        self.draw_deadband_indicator()
        
        # Draw force visualization
        if hasattr(self.pid, 'state') and self.pid.state.output != 0:
            self.draw_force_arrow()
        
        # Draw control panel
        self.control_panel.draw(self.screen)
        
        # Draw PID state info
        self.draw_pid_info()
        
        # Draw deadband status
        self.draw_deadband_status()
        
        # Draw component bars
        self.draw_component_bars()
        
        # Draw graphs
        self.graph_plotter.draw(self.screen)
        
        # No need to draw instructions anymore as we have UI controls
        
        pygame.display.flip()
        
    def draw_wind_indicator(self):
        """Draw wind direction and strength indicator"""
        if abs(self.platform.wind_force) > 0.01:
            # Position for wind indicator (top of simulation area)
            wind_y = 50
            wind_x = self.sim_width // 2
            
            # Scale wind force for visualization
            wind_scale = 10
            wind_length = int(self.platform.wind_force * wind_scale)
            
            # Draw wind arrow
            arrow_start = (wind_x, wind_y)
            arrow_end = (wind_x + wind_length, wind_y)
            
            # Wind color (blue-ish)
            wind_color = (100, 150, 255)
            
            pygame.draw.line(self.screen, wind_color, arrow_start, arrow_end, 4)
            
            # Arrow head
            if wind_length != 0:
                sign = 1 if wind_length > 0 else -1
                pygame.draw.polygon(self.screen, wind_color, [
                    arrow_end,
                    (arrow_end[0] - sign * 10, arrow_end[1] - 5),
                    (arrow_end[0] - sign * 10, arrow_end[1] + 5)
                ])
            
            # Wind label
            wind_text = self.small_font.render(f"Wind: {self.platform.wind_force:.1f}", True, wind_color)
            text_rect = wind_text.get_rect(center=(wind_x, wind_y - 20))
            self.screen.blit(wind_text, text_rect)
    
    def draw_deadband_indicator(self):
        """Draw deadband zone indicator"""
        # Draw a subtle shaded area around center to show deadband
        deadband_pixels = 200  # Visual representation of deadband zone
        deadband_rect = pygame.Rect(
            self.center_x - deadband_pixels,
            self.sim_height - 150,
            2 * deadband_pixels,
            120
        )
        deadband_surface = pygame.Surface((deadband_rect.width, deadband_rect.height))
        deadband_surface.set_alpha(60)  # More visible
        deadband_surface.fill((255, 150, 150))
        self.screen.blit(deadband_surface, deadband_rect)
        
        # Label
        deadband_text = self.small_font.render("Deadband Zone", True, (200, 100, 100))
        text_rect = deadband_text.get_rect(center=(self.center_x, self.sim_height - 170))
        self.screen.blit(deadband_text, text_rect)
    
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
        y_offset = 480  # Move down more to avoid overlap with controls and buttons
        
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
        
    def draw_deadband_status(self):
        """Show if platform is stuck in deadband"""
        if hasattr(self.pid, 'state'):
            total_force = self.pid.state.output + self.platform.wind_force
            if abs(total_force) < 5.0 and abs(self.platform.velocity) < 0.5:
                # In deadband
                status_text = self.font.render("STUCK IN DEADBAND", True, (255, 0, 0))
                text_rect = status_text.get_rect(center=(self.center_x, self.sim_height - 200))
                self.screen.blit(status_text, text_rect)
    
    def draw_component_bars(self):
        """Draw visual bars for PID components"""
        if not hasattr(self.pid, 'state'):
            return
            
        bar_x = self.sim_width + 40  # Move right to make room for labels
        bar_y = 720  # Move down to avoid overlap with PID state text
        bar_width = 380
        bar_height = 25
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
        bar_y += 35
        self.draw_bar(bar_x, bar_y, bar_width, bar_height,
                     i_term, max_value, (150, 0, 0), "I")
        
        # D bar
        bar_y += 35
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
        self.screen.blit(label_text, (x - 25, y))  # Adjust label position
        
    def reset_simulation(self):
        """Reset simulation to initial state"""
        # Reset platform position
        self.platform.set_position(self.center_x)
        
        # Reset PID controller state
        self.pid.reset()
        
        # Reset graphs
        self.graph_plotter.reset()
        
        # Reset time
        self.simulation_time = 0.0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Only handle clicks in simulation area
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x < self.sim_width and mouse_y < self.sim_height:
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
                # Update wind
                if 'wind' in changed:
                    self.platform.wind_force = changed['wind']
                # Update enabled states
                if 'kp_enabled' in changed:
                    self.pid_enabled['kp'] = changed['kp_enabled']
                if 'ki_enabled' in changed:
                    self.pid_enabled['ki'] = changed['ki_enabled']
                if 'kd_enabled' in changed:
                    self.pid_enabled['kd'] = changed['kd_enabled']
                # Update simulation speed
                if 'speed' in changed:
                    self.simulation_speed = changed['speed']
                # Handle reset buttons
                if 'reset_graphs' in changed:
                    self.graph_plotter.reset()
                    self.simulation_time = 0.0
                if 'reset_simulation' in changed:
                    self.reset_simulation()
                # Handle zoom buttons
                if 'zoom_in' in changed:
                    self.graph_plotter.zoom_in_y()
                    self.graph_plotter.update()
                if 'zoom_out' in changed:
                    self.graph_plotter.zoom_out_y()
                    self.graph_plotter.update()
                if 'auto_scale' in changed:
                    self.graph_plotter.auto_scale()
                    self.graph_plotter.update()
                
    def run(self):
        while self.running:
            self.handle_events()
            
            # PID control with simulation speed
            sim_dt = self.dt * self.simulation_speed
            
            force = self.pid.update(
                setpoint=self.center_x,
                current_value=self.platform.get_position(),
                dt=sim_dt,
                enabled=self.pid_enabled
            )
            self.platform.apply_force(force)
            
            self.platform.update(sim_dt)
            
            # Update simulation time
            self.simulation_time += sim_dt
            
            # Collect data for graphs
            p_component, i_component, d_component = self.pid.get_components()
            
            # Apply enabled states to components
            if not self.pid_enabled.get('kp', True):
                p_component = 0
            if not self.pid_enabled.get('ki', True):
                i_component = 0
            if not self.pid_enabled.get('kd', True):
                d_component = 0
            
            self.graph_plotter.add_data(
                time=self.simulation_time,
                error=self.pid.state.error,
                output=self.pid.state.output,
                p_component=p_component,
                i_component=i_component,
                d_component=d_component
            )
            
            # Update graphs periodically (based on real time)
            real_time = time.time() - self.start_time
            if real_time - self.last_graph_update > self.graph_update_interval:
                self.graph_plotter.update()
                self.last_graph_update = real_time
            
            self.draw()
            self.clock.tick(self.config.fps)
        
        pygame.quit()


if __name__ == "__main__":
    simulator = PIDSimulator()
    simulator.run()