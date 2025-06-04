# PID Controller Simulation

An interactive Python simulation for understanding PID (Proportional-Integral-Derivative) control systems. This educational tool visualizes how each component of a PID controller affects system behavior in real-time.

## Features

### Interactive Simulation
- **Click-to-position platform**: Click anywhere in the simulation area to instantly move the platform
- **Real-time visualization**: See the platform respond to PID control in real-time
- **Adjustable parameters**: Modify all PID gains, mass, wind force, and simulation speed on the fly
- **Visual feedback**: Force arrows, wind indicators, and deadband zones clearly show what's happening

### PID Components
- **Proportional (P)**: Responds to current error
- **Integral (I)**: Accumulates error over time to eliminate steady-state errors
- **Derivative (D)**: Responds to rate of change to reduce overshoot
- Each component can be individually enabled/disabled to see its effect

### Advanced Physics
- **Wind disturbance**: Constant external force (-20 to +20 units) simulating real-world disturbances
- **Deadband zone**: Simulates real-world control system imperfections where small forces are ineffective
- **Variable mass**: Adjust platform mass (0.1 to 10.0) to see how system inertia affects control
- **Damping**: Realistic velocity-dependent resistance

### Real-time Graphs
- **Error plot**: Shows deviation from setpoint over time
- **Control output plot**: Displays total control force and individual P, I, D components
- **Auto-scaling**: Graphs automatically adjust scale to keep data visible (can be disabled)
- **Manual zoom controls**: Zoom in/out on Y-axis for detailed analysis
- **20-second sliding window**: Shows recent history while maintaining readability

### Control Panel
- **PID Gains**:
  - Kp (Proportional): 0-20 (default: 5.0)
  - Ki (Integral): 0-3 (default: 0.5)
  - Kd (Derivative): 0-10 (default: 2.0)
- **System Parameters**:
  - Mass: 0.1-10 (default: 1.0)
  - Wind Force: -20 to +20 (default: 0.0)
  - Simulation Speed: 0.5x-5x (default: 2.2x)
- **Controls**:
  - Enable/disable individual PID components
  - Reset graphs or entire simulation
  - Zoom controls for graphs

## Installation

1. Clone the repository:
```bash
git clone https://github.com/krinkin/pid-simulation.git
cd pid-simulation
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the simulation:
```bash
python main.py
```

### Basic Operation
1. **Click** anywhere in the simulation area to move the platform
2. The PID controller will automatically try to return the platform to center
3. Adjust sliders to see how different parameters affect the response

### Understanding PID Control

#### P-only Control
- Disable I and D components
- The platform responds proportionally to error
- May not reach exactly center (steady-state error)
- No overshoot but possibly slow response

#### PI Control
- Enable P and I, disable D
- Integral component eliminates steady-state error
- May cause overshoot and oscillation
- Essential when external forces (wind) are present

#### PID Control
- Enable all components
- D component reduces overshoot and oscillation
- Fastest settling time with proper tuning
- Most robust to disturbances

### Experiments to Try

1. **Steady-State Error Demo**:
   - Set Kp=5, Ki=0, Kd=0
   - Add wind force (5-10 units)
   - Notice platform doesn't quite reach center
   - Enable Ki (0.5) - watch it eliminate the error

2. **Deadband Effect**:
   - Use moderate gains (Kp=3, Ki=0, Kd=0)
   - Set small wind force (2-3 units)
   - Platform gets stuck in deadband zone
   - Add integral control to push through

3. **Mass Effect**:
   - Start with default PID values
   - Increase mass to 5.0
   - System becomes sluggish
   - Increase gains to compensate

4. **Overshoot and Oscillation**:
   - Set high Kp (15-20), Ki=0, Kd=0
   - Click far from center
   - Observe aggressive overshoot
   - Add D component to dampen

## Technical Details

### Physics Model
- Platform dynamics: F = ma with velocity damping
- Deadband: Forces below 5.0 units are only 10% effective
- Wind: Constant external force applied to platform
- Damping coefficient: 0.1 (velocity-proportional)

### Graph Specifications
- Error range: ±2 pixels (default, auto-scales)
- Output range: ±100 units (default, auto-scales)
- Time window: 20 seconds
- Update rate: 20 Hz
- Auto-zoom: Enabled by default

### File Structure
```
pid-demo/
├── main.py              # Main simulation loop and window management
├── physics_platform.py  # Platform physics and dynamics
├── pid_controller.py    # PID control algorithm implementation
├── ui_controls.py       # Sliders, buttons, and checkboxes
├── graph_plotter.py     # Real-time plotting with matplotlib
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Requirements
- Python 3.8+
- pygame 2.5.2
- numpy 1.24.3
- matplotlib 3.7.1

## Educational Value

This simulation helps understand:
- How each PID component contributes to control
- Why integral control is necessary for steady-state accuracy
- How derivative control prevents overshoot
- The effect of system parameters on control performance
- Real-world challenges like deadbands and external disturbances

## Keyboard Shortcuts
- None currently implemented (all controls via GUI)

## Known Limitations
- Single axis (horizontal) control only
- Simplified physics model
- No noise simulation
- No control saturation limits (except deadband)

## Future Enhancements
- 2D control (X-Y platform)
- Noise and measurement uncertainty
- Different control algorithms (PD, PI, etc.)
- Automatic tuning methods
- Save/load parameter sets
- Export graph data

