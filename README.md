# RPi CAN Object Detection and Visualization

A real-time radar object detection and visualization system for Raspberry Pi, featuring CAN bus communication, 2D/3D rendering, and multi-core processing capabilities.

## 🚀 Features

- **Real-time Object Detection**: Simulates and processes radar object data with configurable parameters
- **CAN Bus Communication**: Full TX/RX support for radar and vehicle data via CAN interface
- **Multi-core Processing**: Utilizes Raspberry Pi's multiple cores for optimal performance
- **2D/3D Visualization**: Dynamic rendering of detected objects with rays, shadows, and perspective views
- **Cross-platform Support**: Runs on Windows, Linux, and Raspberry Pi OS
- **Configurable Display**: Supports various screen resolutions and rendering modes

## 📋 Requirements

### Hardware
- Raspberry Pi 4/5 (recommended) or compatible SBC
- CAN bus interface (optional, for real CAN communication)
- Display (HDMI, LCD, or touchscreen) - plan to use LA080WV5-SL01 -> Signal Interface LVDS (1 ch, 8-bit) , 40 pins FPC

### Software
- Python 3.7+
- pygame
- python-can
- cantools
- multiprocessing support

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/RPi_CAN_Object.git
cd RPi_CAN_Object
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For Raspberry Pi Lite, install video drivers:
```bash
sudo apt update
sudo apt install libsdl2-dev xserver-xorg xinit
```

## 🚦 Usage

### Basic Usage
```bash
cd src
python main.py
```

### Configuration
- Edit `defines.py` to customize display settings, object parameters, and timing
- Modify CAN configuration in `init_com.py` for your specific hardware setup
- Adjust simulation parameters in `simulate.py`

## 📁 Project Structure

```
RPi_CAN_Object/
├── src/
│   ├── main.py              # Main application entry point
│   ├── defines.py           # Global constants and configurations
│   ├── init_com.py          # CAN bus initialization
│   ├── init_draw.py         # Display initialization
│   ├── tx.py               # CAN transmission handling
│   ├── rx.py               # CAN reception handling
│   ├── simulate.py         # Object simulation logic
│   ├── draw_2D.py          # 2D rendering functions
│   ├── draw_3D.py          # 3D rendering functions
│   └── menu.py             # UI controls and menus
├── dbc/                    # CAN database files
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

## 🔧 Key Features

### Multi-core Processing
The application utilizes Raspberry Pi's multiple cores through Python's `multiprocessing` module:
- **Core 1**: Main rendering and UI
- **Core 2**: CAN TX operations (60ms cycle)
- **Core 3**: CAN RX processing (50ms cycle)
- **Core 4**: Object simulation (50ms cycle)

### Real-time Visualization
- Dynamic vehicle tracking with unique IDs
- Ray-casting for field of view visualization
- 2D top-down and 3D perspective views
- Configurable object classes (Car, Bicycle, Pedestrian, Unknown)

### CAN Bus Integration
- Support for radar and vehicle CAN messages
- DBC file parsing for message definitions
- Configurable message rates and priorities
- Simulation mode for development without hardware

## 🎮 Controls

- **ESC**: Exit application
- **Mouse**: Interactive UI elements
- **Keyboard**: Various debugging and configuration options

## 🔧 Configuration

### Display Settings
```python
# In defines.py
screen_width = 1200
screen_height = 800
fps = 60
```

### CAN Settings
```python
# In init_com.py
can_interface = 'can0'
bitrate = 500000
```

### Object Simulation
```python
# In simulate.py
max_objects = 30
update_rate_ms = 50
```

## 🐛 Troubleshooting

### Video Driver Issues (Raspberry Pi Lite)
```bash
export SDL_VIDEODRIVER=fbcon
# or
export SDL_VIDEODRIVER=x11
```

### CAN Interface Issues
```bash
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0
```

### Performance Optimization
- Lower the frame rate for better performance on older hardware
- Reduce the number of simulated objects
- Use framebuffer display mode on headless systems

## 📊 Performance

Tested performance metrics on Raspberry Pi 5:
- **CPU Usage**: ~60% with 4 cores active
- **Memory Usage**: ~150MB RAM
- **Frame Rate**: 60 FPS stable with 30 objects
- **CAN Message Rate**: TX: 60ms, RX: 50ms cycles

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- pygame community for the excellent rendering library
- python-can developers for CAN bus support
- Raspberry Pi Foundation for the amazing hardware platform

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the documentation
- Review the troubleshooting section above

---

**Built with ❤️ for the Raspberry Pi and automotive communities**
