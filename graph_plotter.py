import pygame
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
from collections import deque
from typing import Tuple


class GraphPlotter:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 max_points: int = 600, time_window: float = 20.0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_points = max_points
        self.time_window = time_window
        
        # Scale ranges - can be adjusted
        self.error_scale = 2  # pixels - default range for error (-2 to 2)
        self.output_scale = 100  # force units
        self.error_range = (-self.error_scale, self.error_scale)
        self.output_range = (-self.output_scale, self.output_scale)
        
        # Data storage - no maxlen, we'll manage the window ourselves
        self.time_data = []
        self.error_data = []
        self.output_data = []
        self.p_data = []
        self.i_data = []
        self.d_data = []
        
        # Time tracking
        self.start_time = 0
        self.current_time = 0
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(width/100, height/100), dpi=100)
        self.fig.patch.set_facecolor('#f0f0f0')
        
        # Configure axes
        self.ax1.set_facecolor('#fafafa')
        self.ax2.set_facecolor('#fafafa')
        
        self.ax1.grid(True, alpha=0.3)
        self.ax2.grid(True, alpha=0.3)
        
        self.ax1.set_ylabel('Error', fontsize=12)
        self.ax2.set_ylabel('Control Output', fontsize=12)
        self.ax2.set_xlabel('Time (s)', fontsize=12)
        
        # Set tick label size
        self.ax1.tick_params(labelsize=10)
        self.ax2.tick_params(labelsize=10)
        
        # Adjust layout
        self.fig.tight_layout(pad=1.0)
        
        # Create canvas
        self.canvas = FigureCanvasAgg(self.fig)
        
        # Surface for blitting
        self.surface = None
        
        # Auto-zoom mode
        self.auto_zoom_enabled = True
        
    def add_data(self, time: float, error: float, output: float, 
                 p_component: float, i_component: float, d_component: float):
        """Add new data point"""
        if len(self.time_data) == 0:
            self.start_time = time
            
        self.current_time = time - self.start_time
        self.time_data.append(self.current_time)
        self.error_data.append(error)
        self.output_data.append(output)
        self.p_data.append(p_component)
        self.i_data.append(i_component)
        self.d_data.append(d_component)
        
        # Auto-adjust scale if auto-zoom is enabled
        if self.auto_zoom_enabled:
            # For error
            if abs(error) > self.error_scale * 0.95:
                self.error_scale = abs(error) * 1.2
                self.error_range = (-self.error_scale, self.error_scale)
            
            # For output
            max_output_value = max(abs(output), abs(p_component), abs(i_component), abs(d_component))
            if max_output_value > self.output_scale * 0.95:
                self.output_scale = max_output_value * 1.2
                self.output_range = (-self.output_scale, self.output_scale)
        
    def update(self):
        """Update the plots"""
        if len(self.time_data) < 2:
            return
            
        # Clear axes
        self.ax1.clear()
        self.ax2.clear()
        
        # Convert to numpy arrays
        time_array = np.array(self.time_data)
        
        # Filter data to only show points within the display window
        if self.current_time > self.time_window:
            min_time = self.current_time - self.time_window
            mask = time_array >= min_time
            time_array = time_array[mask]
            error_array = np.array(self.error_data)[mask]
            output_array = np.array(self.output_data)[mask]
            p_array = np.array(self.p_data)[mask]
            i_array = np.array(self.i_data)[mask]
            d_array = np.array(self.d_data)[mask]
        else:
            error_array = np.array(self.error_data)
            output_array = np.array(self.output_data)
            p_array = np.array(self.p_data)
            i_array = np.array(self.i_data)
            d_array = np.array(self.d_data)
        
        # Plot error
        self.ax1.plot(time_array, error_array, 'b-', linewidth=2, label='Error')
        self.ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.ax1.set_ylabel('Error (pixels)', fontsize=12)
        self.ax1.set_ylim(self.error_range)
        self.ax1.grid(True, alpha=0.3)
        self.ax1.legend(loc='upper left', fontsize=10)
        
        # Plot control output and components
        self.ax2.plot(time_array, output_array, 'k-', linewidth=2, label='Total')
        self.ax2.plot(time_array, p_array, 'g--', alpha=0.7, label='P')
        self.ax2.plot(time_array, i_array, 'r--', alpha=0.7, label='I')
        self.ax2.plot(time_array, d_array, 'b--', alpha=0.7, label='D')
        self.ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.ax2.set_ylabel('Control Output (N)', fontsize=12)
        self.ax2.set_xlabel('Time (s)', fontsize=12)
        self.ax2.set_ylim(self.output_range)
        self.ax2.grid(True, alpha=0.3)
        self.ax2.legend(loc='upper left', fontsize=10)
        
        # Set x-axis limits - always show a fixed time window
        if self.current_time <= self.time_window:
            # Show from 0 to time_window when we haven't filled the window yet
            self.ax1.set_xlim(0, self.time_window)
            self.ax2.set_xlim(0, self.time_window)
        else:
            # Show sliding window of the most recent data
            self.ax1.set_xlim(self.current_time - self.time_window, self.current_time)
            self.ax2.set_xlim(self.current_time - self.time_window, self.current_time)
        
        # Set tick label size
        self.ax1.tick_params(labelsize=10)
        self.ax2.tick_params(labelsize=10)
        
        # Render to pygame surface
        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.buffer_rgba()
        size = self.canvas.get_width_height()
        
        #raw_data = renderer.buffer_rgba()
        self.surface = pygame.image.frombuffer(raw_data, size, "RGBA")

        #self.surface = pygame.image.fromstring(raw_data, size, "RGB")
        
    def draw(self, screen: pygame.Surface):
        """Draw the graphs to the screen"""
        if self.surface:
            screen.blit(self.surface, (self.x, self.y))
        else:
            # Draw placeholder
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(screen, (200, 200, 200), rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 2)
            
    def reset(self):
        """Clear all data"""
        self.time_data = []
        self.error_data = []
        self.output_data = []
        self.p_data = []
        self.i_data = []
        self.d_data = []
        self.start_time = 0
        self.current_time = 0
        
    def zoom_in_y(self):
        """Zoom in on Y axes (reduce scale)"""
        self.auto_zoom_enabled = False  # Disable auto-zoom when manually zooming
        self.error_scale = max(1, self.error_scale * 0.8)
        self.output_scale = max(10, self.output_scale * 0.8)
        self.error_range = (-self.error_scale, self.error_scale)
        self.output_range = (-self.output_scale, self.output_scale)
        
    def zoom_out_y(self):
        """Zoom out on Y axes (increase scale)"""
        self.auto_zoom_enabled = False  # Disable auto-zoom when manually zooming
        self.error_scale = min(2000, self.error_scale * 1.25)
        self.output_scale = min(2000, self.output_scale * 1.25)
        self.error_range = (-self.error_scale, self.error_scale)
        self.output_range = (-self.output_scale, self.output_scale)
        
    def auto_scale(self):
        """Auto-scale Y axes based on data and re-enable auto-zoom"""
        self.auto_zoom_enabled = True  # Re-enable auto-zoom
        
        if len(self.error_data) > 0:
            max_error = max(abs(min(self.error_data)), abs(max(self.error_data)))
            self.error_scale = max(1, min(2000, max_error * 1.2))
            self.error_range = (-self.error_scale, self.error_scale)
            
        if len(self.output_data) > 0:
            all_outputs = self.output_data + self.p_data + self.i_data + self.d_data
            max_output = max(abs(min(all_outputs)), abs(max(all_outputs)))
            self.output_scale = max(10, min(2000, max_output * 1.2))
            self.output_range = (-self.output_scale, self.output_scale)
