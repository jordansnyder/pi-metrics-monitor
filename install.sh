#/bin/bash
# Install pip
sudo apt-get install pip3

# Install prometheus-client
sudo pip3 install prometheus-client

# Install the python3-systemd package for Journal integration
sudo apt-get install python3-systemd

sudo mkdir /opt/pi-metrics-service
sudo mv $(pwd)/metrics_monitor.py /opt/pi-metrics-service/
sudo mv $(pwd)/pi-metrics-monitor.service /etc/systemd/system/

# Enable and start the sensor-metrics.service
sudo systemctl enable pi-metrics-monitor.service
sudo systemctl start pi-metrics-monitor.service
