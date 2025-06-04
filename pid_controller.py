import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class PIDState:
    """Holds the current state of PID controller"""
    error: float = 0.0
    integral: float = 0.0
    derivative: float = 0.0
    last_error: float = 0.0
    output: float = 0.0


class PIDController:
    def __init__(self, kp: float = 1.0, ki: float = 0.0, kd: float = 0.0):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        
        self.state = PIDState()
        
        # Anti-windup limits
        self.integral_limit = 1000.0
        
        # Output limits
        self.output_limit = 100.0
        
    def update(self, setpoint: float, current_value: float, dt: float) -> float:
        """
        Calculate PID output
        
        Args:
            setpoint: Target value
            current_value: Current measured value
            dt: Time step
            
        Returns:
            Control output (force to apply)
        """
        # Calculate error
        self.state.error = setpoint - current_value
        
        # Proportional term
        p_term = self.kp * self.state.error
        
        # Integral term with anti-windup
        self.state.integral += self.state.error * dt
        self.state.integral = np.clip(
            self.state.integral, 
            -self.integral_limit, 
            self.integral_limit
        )
        i_term = self.ki * self.state.integral
        
        # Derivative term
        if dt > 0:
            self.state.derivative = (self.state.error - self.state.last_error) / dt
        else:
            self.state.derivative = 0.0
        d_term = self.kd * self.state.derivative
        
        # Calculate total output
        self.state.output = p_term + i_term + d_term
        
        # Apply output limits
        self.state.output = np.clip(
            self.state.output,
            -self.output_limit,
            self.output_limit
        )
        
        # Store error for next iteration
        self.state.last_error = self.state.error
        
        return self.state.output
    
    def reset(self):
        """Reset the controller state"""
        self.state = PIDState()
        
    def set_gains(self, kp: float, ki: float, kd: float):
        """Update PID gains"""
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
    def get_components(self) -> tuple:
        """Get individual PID components for visualization"""
        p_term = self.kp * self.state.error
        i_term = self.ki * self.state.integral
        d_term = self.kd * self.state.derivative
        return p_term, i_term, d_term