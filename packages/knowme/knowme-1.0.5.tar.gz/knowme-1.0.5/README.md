# KnowMe

A fast, offline command-line tool that displays detailed system information with a classic, neofetch-style ASCII logo.

## Features

- 🚀 **Fast & Offline**: No internet connection required
- 🎨 **Beautiful ASCII Art**: OS-specific logos and colorful output
- 📊 **Comprehensive Info**: CPU, Memory, Storage, Network, and more
- 🔧 **Cross-Platform**: Works on Linux, macOS, and Windows
- 💻 **Lightweight**: Minimal dependencies and resource usage

## Installation

### From PyPI (Recommended)

```bash
pip install knowme
```

### From Source

```bash
git clone https://github.com/mehtahrishi/knowme.git
cd knowme
pip install .
```

### Development Installation

```bash
git clone https://github.com/mehtahrishi/knowme.git
cd knowme
pip install -e .
```

## Usage

Simply run the command:

```bash
knowme
```

This will display your system information in a beautiful two-column layout with an ASCII logo.

## System Information Displayed

- **Operating System**: Name, version, and architecture
- **Kernel**: Kernel version and release info
- **CPU**: Model, cores, threads, and current frequency
- **Memory**: Total, used, and available RAM
- **Storage**: Disk usage for all mounted drives
- **Network**: Active interfaces and IP addresses
- **GPU**: Graphics card information (if available)
- **Display**: Screen resolution and refresh rate
- **Uptime**: System uptime
- **Shell**: Current shell and version
- **Terminal**: Terminal emulator information

## Requirements

- Python 3.7 or higher
- Works on Linux, macOS, and Windows

## Dependencies

- `psutil` - System and process utilities
- `distro` - Linux distribution information
- `py-cpuinfo` - CPU information
- `requests` - HTTP library
- `gputil` - GPU utilities
- `screeninfo` - Display information
- `ifaddr` - Network interface addresses

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Inspired by neofetch and other system information tools.
