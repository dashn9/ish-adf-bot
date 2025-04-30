# 🕹️ Web Page Human Behavior Simulation Bot

A sophisticated automation framework that precisely mimics human behavior on web pages. Unlike traditional web automation tools, this bot incorporates advanced human behavior mechanics, natural interaction patterns, and randomized decision-making to create truly authentic web browsing sessions.

## 🎯 Core Capabilities

- **Natural Mouse Movement**: Implements human-like cursor trajectories with realistic acceleration, deceleration, and occasional imperfect movements
- **Intelligent Page Interaction**: 
  - Simulates natural reading patterns with variable scroll speeds
  - Randomly hovers over interesting elements
  - Exhibits human-like focus and attention spans
  - Implements natural typing patterns with realistic delays
- **Smart Ad Engagement**:
  - Probabilistic ad interaction based on configurable user profiles
  - Natural dwell time on ad content
  - Realistic click-through patterns
- **Dynamic Identity System**:
  - Configurable user personas with consistent behaviors
  - Device-specific interaction patterns (mobile vs desktop)
  - Timezone-aware behavior patterns

## 🚀 Features

- **Advanced Human Simulation**:
  - Randomized mouse movement with natural acceleration curves
  - Variable scrolling speeds and patterns
  - Natural typing rhythms and occasional mistakes
  - Realistic waiting times between actions
  - Attention span simulation with dynamic focus points

- **Browser Support**:
  - Chrome browser automation via nodriver
  - Screen resolution-aware interactions
  - Timezone and locale-based patterns

- **Interaction Capabilities**:
  - Form filling with human-like typing patterns
  - Natural navigation through page elements
  - Contextual element interaction
  - Ad engagement with realistic timing
  - Dynamic content handling with smart waits

- **Infrastructure**:
  - Dockerized deployment
  - GUI mode for anti detection
  - Proxy support
  - Detailed logging and monitoring
  - Configurable behavior profiles

## ⚡ Quickstart

### With Docker (Recommended)

```bash
docker build -t human-behavior-bot .
docker run --rm -it human-behavior-bot
```

### Manual Setup (Python 3.12+)

```bash
# 1. Install dependencies
pip install -r requirements.txt


# 3. Run the bot
python run.py
```

## 🛠️ Configuration

### Setup Configuration

1. Create a `config.ini` file in the `configs` directory based on `configs/example.config.ini`
2. Configure your settings for:
   - Screen resolution and display settings
   - Browser paths and extensions
   - Bot behavior parameters
   - Proxy and VPN settings
   - Identity management

### Human Behavior Simulation

The bot uses a sophisticated identity system to simulate realistic human behavior:

- **Device & Browser Fingerprinting**:
  - Canvas fingerprinting with unique offsets
  - Audio context fingerprinting
  - Font fingerprinting
  - WebGL fingerprinting
  - Hardware concurrency and memory details
  - GPU vendor and renderer information

- **User Behavior Patterns**:
  - Reading speed variations
  - Mouse movement patterns and delta tracking
  - Page depth exploration
  - Language preferences
  - Cookie management
  - Referral tracking

- **Ad Interaction Simulation**:
  - Configurable click probabilities
  - Keyword-based engagement
  - Type-specific ad interactions
  - Natural dwell times

- **Device Characteristics**:
  - Hardware specifications
  - OS and platform details
  - Screen resolution awareness
  - Input device detection (mouse, touch, battery)
  - Browser version and user agent strings

- **Geographic & Network**:
  - Country-specific behavior
  - Proxy and VPN integration
  - Geo-location aware interactions
  - Network fingerprinting

### Advanced Configuration

For detailed configuration options, refer to:
- `configs/example.config.ini` - Base configuration template
- `constants/bot_constants.py` - Core behavior parameters
- `humanbehaviourmechanics/` - Detailed interaction patterns

## 🧩 Project Structure

```
.
├── run.py                # Main entry point
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── constants/           # Configuration and constants
│   ├── config.py       # Core settings
│   └── bot_constants.py # Behavior parameters
├── bots/               # Core bot implementation
├── datacontroller/     # Data management
├── identity/           # User profile simulation
├── humanbehaviourmechanics/ # Human behavior patterns
│   ├── mouse_movement.py   # Natural cursor movement
│   ├── scroll_behavior.py  # Reading patterns
│   └── typing_patterns.py  # Human-like input
└── ...
```

## 📝 Usage & Customization

### Basic Usage

- Set target URLs in `run.py` or configure dynamic URL sources
- Adjust behavior parameters in configuration files

### Advanced Customization

- Extend `Identity` class for custom user profiles
- Modify interaction patterns in `humanbehaviourmechanics/`
- Implement custom behavior modules in `bots/`
- Use `DataController` for complex data management

### Monitoring & Debugging

- Enable `DEBUG` for detailed logging
- Monitor network activity with `PRINT_NETWORK`
- Use GUI mode for visual behavior verification

## 🤝 Contributing

We welcome contributions! Please:

1. Open an issue to discuss proposed changes
2. Fork the repository and create a feature branch
3. Submit a pull request with detailed description
4. Ensure all tests pass and code meets quality standards

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 💡 Pro Tips

- Use Docker for consistent environment across deployments
- Start with existing behavior profiles and customize gradually
- Monitor CPU/memory usage when running multiple instances
- Add logging for behavior analysis and debugging
- Consider adding a demo video showing the natural interactions


## Deployment
- Please check my repos to find the Kubernetes Deployment Repo
 - Utilities to generate your Bot Identites
 - Backend Server to feed Identities to the bot
 - Extensions to complete functionalities