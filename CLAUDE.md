# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Raspberry Pi system monitoring service that exposes CPU/GPU temperatures, RAM usage, and network statistics as Prometheus metrics. It runs as a systemd service and serves metrics on port 8000.

## Architecture

The system consists of three main components:

1. **metrics_monitor.py** - Main Python script that:
   - Reads GPU temperature via `vcgencmd measure_temp` command
   - Reads CPU temperature from `/sys/class/thermal/thermal_zone0/temp`
   - Reads RAM usage from `/proc/meminfo` (total, available, used, percent)
   - Reads network statistics from `/proc/net/dev` (bytes, packets, errors per interface)
   - Exposes metrics via Prometheus client library on port 8000
   - Logs to systemd journal
   - Runs in infinite loop with 5-second intervals

2. **pi-metrics-monitor.service** - Systemd service unit that:
   - Runs the Python script from `/opt/pi-metrics-service/`
   - Configured for automatic restart
   - Starts after network is available

3. **install.sh** - Installation script that:
   - Installs dependencies via apt-get (python3-prometheus-client, python3-systemd)
   - Copies files to `/opt/pi-metrics-service/` and `/etc/systemd/system/`
   - Enables and starts the systemd service

## Common Commands

### Installation
```bash
sudo ./install.sh
```

### Service Management
```bash
# Check service status
sudo systemctl status pi-metrics-monitor.service

# Restart service
sudo systemctl restart pi-metrics-monitor.service

# View logs
sudo journalctl -u pi-metrics-monitor.service -f
```

### Testing Metrics Endpoint
```bash
# View metrics locally
curl localhost:8000

# View metrics from another machine
curl <RASPBERRY_PI_IP>:8000
```

### Development Testing
```bash
# Run script directly (without systemd)
python3 ./metrics_monitor.py

# Test sensor reading
vcgencmd measure_temp
cat /sys/class/thermal/thermal_zone0/temp
```

## Important Notes

- Designed to run on Raspberry Pi (depends on Pi-specific commands and files)
- Requires root/sudo permissions for installation and service management
- GPU reading uses `vcgencmd` which is Raspberry Pi specific
- CPU reading assumes thermal zone at `/sys/class/thermal/thermal_zone0/temp`

### Exposed Prometheus Metrics

**Temperature Metrics:**
- `gpu_temperature` - GPU temperature in Celsius
- `cpu_temperature` - CPU temperature in Celsius

**Memory Metrics:**
- `memory_total_bytes` - Total system memory in bytes
- `memory_available_bytes` - Available memory in bytes
- `memory_used_bytes` - Used memory in bytes
- `memory_used_percent` - Memory usage percentage

**Network Metrics (labeled by interface):**
- `network_rx_bytes_total{interface="..."}` - Total bytes received
- `network_tx_bytes_total{interface="..."}` - Total bytes transmitted
- `network_rx_packets_total{interface="..."}` - Total packets received
- `network_tx_packets_total{interface="..."}` - Total packets transmitted
- `network_rx_errors_total{interface="..."}` - Total receive errors
- `network_tx_errors_total{interface="..."}` - Total transmit errors
