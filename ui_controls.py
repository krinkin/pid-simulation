import pygame
from typing import Callable, Optional, Tuple


class Slider:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_val: float, max_val: float, initial_val: float,
                 label: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        
        # Visual properties
        self.bg_color = (200, 200, 200)
        self.fg_color = (100, 100, 200)
        self.handle_color = (50, 50, 150)
        self.text_color = (0, 0, 0)
        
        # State
        self.dragging = False
        
        # Font
        self.font = pygame.font.Font(None, 28)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events, return True if value changed"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value(event.pos[0])
                return True
                
        return False
    
    def _update_value(self, mouse_x: int):
        """Update value based on mouse position"""
        # Clamp mouse position to slider bounds
        x = max(self.rect.left, min(mouse_x, self.rect.right))
        
        # Calculate value
        ratio = (x - self.rect.left) / self.rect.width
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        
    def draw(self, screen: pygame.Surface):
        """Draw the slider"""
        # Draw background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)
        
        # Draw filled portion
        fill_ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        fill_width = int(self.rect.width * fill_ratio)
        fill_rect = pygame.Rect(self.rect.left, self.rect.top, fill_width, self.rect.height)
        pygame.draw.rect(screen, self.fg_color, fill_rect)
        
        # Draw handle
        handle_x = self.rect.left + fill_width
        handle_rect = pygame.Rect(handle_x - 5, self.rect.top - 5, 10, self.rect.height + 10)
        pygame.draw.rect(screen, self.handle_color, handle_rect)
        
        # Draw label and value
        label_text = self.font.render(f"{self.label}: {self.value:.3f}", True, self.text_color)
        screen.blit(label_text, (self.rect.left, self.rect.top - 30))


class Checkbox:
    def __init__(self, x: int, y: int, size: int, label: str, checked: bool = True):
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.checked = checked
        
        # Visual properties
        self.bg_color = (255, 255, 255)
        self.border_color = (100, 100, 100)
        self.check_color = (50, 150, 50)
        self.text_color = (0, 0, 0)
        
        # Font
        self.font = pygame.font.Font(None, 24)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events, return True if value changed"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True
        return False
        
    def draw(self, screen: pygame.Surface):
        """Draw the checkbox"""
        # Draw box background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Draw check mark if checked
        if self.checked:
            # Draw a simple X
            padding = 4
            pygame.draw.line(screen, self.check_color,
                           (self.rect.left + padding, self.rect.top + padding),
                           (self.rect.right - padding, self.rect.bottom - padding), 3)
            pygame.draw.line(screen, self.check_color,
                           (self.rect.right - padding, self.rect.top + padding),
                           (self.rect.left + padding, self.rect.bottom - padding), 3)
        
        # Draw label
        label_text = self.font.render(self.label, True, self.text_color)
        screen.blit(label_text, (self.rect.right + 10, self.rect.centery - label_text.get_height() // 2))
        

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        
        # Visual properties
        self.normal_color = (100, 100, 200)
        self.hover_color = (120, 120, 220)
        self.pressed_color = (80, 80, 180)
        self.text_color = (255, 255, 255)
        
        # State
        self.hovered = False
        self.pressed = False
        
        # Font
        self.font = pygame.font.Font(None, 26)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events, return True if button was clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                return True
            self.pressed = False
            
        return False
        
    def draw(self, screen: pygame.Surface):
        """Draw the button"""
        # Choose color based on state
        if self.pressed:
            color = self.pressed_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.normal_color
            
        # Draw button
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (50, 50, 100), self.rect, 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class ControlPanel:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 400  # Increased width for better layout
        self.padding = 10
        self.slider_height = 20
        self.slider_spacing = 60
        
        # Create sliders with adjusted positions
        slider_x = x + self.padding + 30  # Make room for checkboxes
        self.sliders = {
            'kp': Slider(slider_x, y + self.padding, 
                        self.width - 50, self.slider_height,
                        0.0, 20.0, 5.0, "Kp (Proportional)"),
            'ki': Slider(slider_x, y + self.padding + self.slider_spacing,
                        self.width - 50, self.slider_height,
                        0.0, 3.0, 0.5, "Ki (Integral)"),
            'kd': Slider(slider_x, y + self.padding + 2 * self.slider_spacing,
                        self.width - 50, self.slider_height,
                        0.0, 10.0, 2.0, "Kd (Derivative)"),
            'mass': Slider(x + self.padding, y + self.padding + 3 * self.slider_spacing,
                          self.width - 2 * self.padding, self.slider_height,
                          0.1, 10.0, 1.0, "Mass"),
            'speed': Slider(x + self.padding, y + self.padding + 4 * self.slider_spacing,
                          self.width - 2 * self.padding, self.slider_height,
                          0.5, 5.0, 2.2, "Simulation Speed"),
            'wind': Slider(x + self.padding, y + self.padding + 5 * self.slider_spacing,
                          self.width - 2 * self.padding, self.slider_height,
                          -20.0, 20.0, 0.0, "Wind Force"),
        }
        
        # Create checkboxes for PID components
        checkbox_size = 20
        self.checkboxes = {
            'kp_enabled': Checkbox(x + self.padding, y + self.padding + 5, 
                                  checkbox_size, "", True),
            'ki_enabled': Checkbox(x + self.padding, y + self.padding + self.slider_spacing + 5,
                                  checkbox_size, "", True),
            'kd_enabled': Checkbox(x + self.padding, y + self.padding + 2 * self.slider_spacing + 5,
                                  checkbox_size, "", True),
        }
        
        # Create buttons - first row
        button_width = (self.width - 3 * self.padding) // 2
        self.reset_graphs_button = Button(
            x + self.padding, 
            y + self.padding + 6 * self.slider_spacing,
            button_width,
            30,
            "Reset Graphs"
        )
        
        self.reset_sim_button = Button(
            x + self.padding + button_width + self.padding,
            y + self.padding + 6 * self.slider_spacing,
            button_width,
            30,
            "Reset Simulation"
        )
        
        # Create buttons - second row for graph controls
        button_width_small = (self.width - 4 * self.padding) // 3
        self.zoom_in_button = Button(
            x + self.padding,
            y + self.padding + 6 * self.slider_spacing + 40,
            button_width_small,
            30,
            "Zoom In Y"
        )
        
        self.zoom_out_button = Button(
            x + self.padding + button_width_small + self.padding,
            y + self.padding + 6 * self.slider_spacing + 40,
            button_width_small,
            30,
            "Zoom Out Y"
        )
        
        self.auto_scale_button = Button(
            x + self.padding + 2 * (button_width_small + self.padding),
            y + self.padding + 6 * self.slider_spacing + 40,
            button_width_small,
            30,
            "Auto Scale"
        )
        
        # Background
        self.bg_color = (250, 250, 250)
        self.border_color = (100, 100, 100)
        
        # Calculate total height
        self.height = 7 * self.slider_spacing + 2 * self.padding
        
    def handle_event(self, event: pygame.event.Event) -> dict:
        """Handle events and return dict of changed values"""
        changed = {}
        for name, slider in self.sliders.items():
            if slider.handle_event(event):
                changed[name] = slider.value
        
        for name, checkbox in self.checkboxes.items():
            if checkbox.handle_event(event):
                changed[name] = checkbox.checked
                
        # Handle reset buttons
        if self.reset_graphs_button.handle_event(event):
            changed['reset_graphs'] = True
            
        if self.reset_sim_button.handle_event(event):
            changed['reset_simulation'] = True
            
        # Handle zoom buttons
        if self.zoom_in_button.handle_event(event):
            changed['zoom_in'] = True
            
        if self.zoom_out_button.handle_event(event):
            changed['zoom_out'] = True
            
        if self.auto_scale_button.handle_event(event):
            changed['auto_scale'] = True
                
        return changed
        
    def draw(self, screen: pygame.Surface):
        """Draw the control panel"""
        # Draw background
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, panel_rect)
        pygame.draw.rect(screen, self.border_color, panel_rect, 2)
        
        # Draw sliders
        for slider in self.sliders.values():
            slider.draw(screen)
            
        # Draw checkboxes
        for checkbox in self.checkboxes.values():
            checkbox.draw(screen)
            
        # Draw all buttons
        self.reset_graphs_button.draw(screen)
        self.reset_sim_button.draw(screen)
        self.zoom_in_button.draw(screen)
        self.zoom_out_button.draw(screen)
        self.auto_scale_button.draw(screen)
            
    def get_values(self) -> dict:
        """Get current values of all sliders and checkboxes"""
        values = {name: slider.value for name, slider in self.sliders.items()}
        values.update({name: checkbox.checked for name, checkbox in self.checkboxes.items()})
        return values