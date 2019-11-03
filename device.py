##### The device just generates data and sends the data to each server. 

import socket
import logging
import time

def device_program(num_servers):
	host = socket.gethostname()  # as both code is running on same pc
	dns_addr = socket.gethostbyname(host)
	port = 12345  # socket server port number

	connected_servers = []

	for i in range(0, num_servers):
		try:
			client_socket = socket.socket()  # instantiate
			# client_socket.connect((dns_addr, port))  # connect to the server
			client_socker.bind('', port)
			connected_servers.append(client_socket)
			print('connected', len(connected_servers))
		except Exception as e:
			logging.warning('No server running on port: %s', port)
			logging.exception('Exception message: %s', e)
			# we start servers on +1 ports
			break
		port += 1
	value = 0
	while True:
		client_socket = connected_servers[0]
		message = str(value)
		value -= 1
		client_socket.send(message.encode())
		time.sleep(2)


if __name__ == '__main__':
	device_program(1)