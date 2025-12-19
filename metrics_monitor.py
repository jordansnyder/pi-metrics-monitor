#!/usr/bin/env python3

import logging
import time

import subprocess
# Import Gauge and start_http_server from prometheus_client
from prometheus_client import Gauge, start_http_server
from systemd.journal import JournalHandler

READ_INTERVAL = 5.0

# Setup logging to the Systemd Journal
log = logging.getLogger('metrics_monitor')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

# Create Prometheus gauges for CPU/GPU temperature
gpuTempGauge = Gauge('gpu_temperature', 'GPU Temperature')
cpuTempGauge = Gauge('cpu_temperature', 'CPU Temperature')

def read_sensors():
	try:
		gpuout = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
		if gpuout.stdout.startswith(b"temp="):
			part = gpuout.stdout[len("temp="):]
			if part.endswith(b"'C\n"):
				gpu = float(part[:len(part) - len("'C\n")])

		cpufile = '/sys/class/thermal/thermal_zone0/temp'
		with open(cpufile) as file:
			data = file.read()
			cpu = int(data) / 1000

		if gpu is not None and cpu is not None:
			gpuTempGauge.set(gpu)
			cpuTempGauge.set(cpu)
			#log.info("GPU Temp: {0:0.1f}*C, CPU Temp: {0:0.1f}*C".format(gpu, cpu))
	except RuntimeError as e:
        	# GPIO access may require sudo permissions
        	# Other RuntimeError exceptions may occur, but
        	# are common.  Just try again.
		log.error("RuntimeError: {}".format(e))
	
	time.sleep(READ_INTERVAL)

if __name__=='__main__':
	# Expose metrics
	metrics_port = 8000
	start_http_server(metrics_port)
	print("Serving sensor metrics on :{}".format(metrics_port))
	log.info("Serving sensor metrics on :{}".format(metrics_port))

	while True:
		read_sensors()
