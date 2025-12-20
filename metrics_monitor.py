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

# Create Prometheus gauges for RAM usage
memTotalGauge = Gauge('memory_total_bytes', 'Total memory in bytes')
memAvailableGauge = Gauge('memory_available_bytes', 'Available memory in bytes')
memUsedGauge = Gauge('memory_used_bytes', 'Used memory in bytes')
memUsedPercentGauge = Gauge('memory_used_percent', 'Used memory percentage')

# Create Prometheus gauges for network statistics (using labels for interface)
netRxBytesGauge = Gauge('network_rx_bytes_total', 'Total bytes received', ['interface'])
netTxBytesGauge = Gauge('network_tx_bytes_total', 'Total bytes transmitted', ['interface'])
netRxPacketsGauge = Gauge('network_rx_packets_total', 'Total packets received', ['interface'])
netTxPacketsGauge = Gauge('network_tx_packets_total', 'Total packets transmitted', ['interface'])
netRxErrorsGauge = Gauge('network_rx_errors_total', 'Total receive errors', ['interface'])
netTxErrorsGauge = Gauge('network_tx_errors_total', 'Total transmit errors', ['interface'])

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

def read_memory():
	try:
		meminfo_file = '/proc/meminfo'
		mem_data = {}

		with open(meminfo_file) as file:
			for line in file:
				parts = line.split(':')
				if len(parts) == 2:
					key = parts[0].strip()
					value = parts[1].strip().split()[0]  # Get numeric value, ignore 'kB'
					mem_data[key] = int(value) * 1024  # Convert kB to bytes

		mem_total = mem_data.get('MemTotal', 0)
		mem_available = mem_data.get('MemAvailable', 0)
		mem_used = mem_total - mem_available
		mem_used_percent = (mem_used / mem_total * 100) if mem_total > 0 else 0

		memTotalGauge.set(mem_total)
		memAvailableGauge.set(mem_available)
		memUsedGauge.set(mem_used)
		memUsedPercentGauge.set(mem_used_percent)

	except Exception as e:
		log.error("Error reading memory: {}".format(e))

def read_network():
	try:
		netdev_file = '/proc/net/dev'

		with open(netdev_file) as file:
			lines = file.readlines()

		# Skip header lines
		for line in lines[2:]:
			parts = line.split(':')
			if len(parts) != 2:
				continue

			interface = parts[0].strip()

			# Skip loopback interface
			if interface == 'lo':
				continue

			stats = parts[1].split()
			if len(stats) >= 16:
				# Format: rx_bytes, rx_packets, rx_errs, rx_drop, rx_fifo, rx_frame, rx_compressed, rx_multicast,
				#         tx_bytes, tx_packets, tx_errs, tx_drop, tx_fifo, tx_colls, tx_carrier, tx_compressed
				rx_bytes = int(stats[0])
				rx_packets = int(stats[1])
				rx_errors = int(stats[2])
				tx_bytes = int(stats[8])
				tx_packets = int(stats[9])
				tx_errors = int(stats[10])

				netRxBytesGauge.labels(interface=interface).set(rx_bytes)
				netTxBytesGauge.labels(interface=interface).set(tx_bytes)
				netRxPacketsGauge.labels(interface=interface).set(rx_packets)
				netTxPacketsGauge.labels(interface=interface).set(tx_packets)
				netRxErrorsGauge.labels(interface=interface).set(rx_errors)
				netTxErrorsGauge.labels(interface=interface).set(tx_errors)

	except Exception as e:
		log.error("Error reading network stats: {}".format(e))

if __name__=='__main__':
	# Expose metrics
	metrics_port = 8000
	start_http_server(metrics_port)
	print("Serving sensor metrics on :{}".format(metrics_port))
	log.info("Serving sensor metrics on :{}".format(metrics_port))

	while True:
		read_sensors()
		read_memory()
		read_network()
		time.sleep(READ_INTERVAL)
