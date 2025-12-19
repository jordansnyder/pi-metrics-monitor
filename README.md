# pi-metrics-monitor
Installs a system service (and dependencies) that will read CPU and GPU temps every 5 seconds, create a Prometheus Gauge object and start an HTTP server on port 8000 so that Prometheus can ingest it. 

You can curl $HOST:8000 or open in a browser to verify that the data is being published.

`sudo ./install.sh`


Check the status of the service:

`sudo systemctl status pi-metrics-monitor.service`
