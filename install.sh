#!/bin/bash

# Install prometheus-client
echo "Install Prometheus Client system-wide..."
sudo pip3 install prometheus-client

# Install the python3-systemd package for Journal integration
echo "Install systemd package for syslog integration"
sudo apt-get install python3-systemd

echo "Create directory for scripts..."
sudo mkdir /opt/pi-metrics-service
sudo cp $(pwd)/metrics_monitor.py /opt/pi-metrics-service/
sudo cp $(pwd)/pi-metrics-monitor.service /etc/systemd/system/

# Enable and start the sensor-metrics.service
sudo systemctl enable pi-metrics-monitor.service
sudo systemctl start pi-metrics-monitor.service
