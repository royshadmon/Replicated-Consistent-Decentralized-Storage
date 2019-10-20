
import socket
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)


def server_program():
	# get the hostname
	host = socket.gethostname()
	dns_addr = socket.gethostbyname(host)
	port = 12345  # initiate port no above 1024

	server_socket = socket.socket()  # get instance
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# look closely. The bind() function takes tuple as argument
	server_socket.bind((dns_addr, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
	server_socket.listen(2)
	conn, address = server_socket.accept()  # accept new connection
	logging.info("Connection from: %s", address)
	storage = []
	while True:
		# receive data stream. it won't accept data packet greater than 1024 bytes
		data = conn.recv(1024).decode()
		data = data.lower()
		if data.endswith('bye') or not data:
			break			
		elif data.split()[0] == 'get':
			msg = storage[int(data.split()[1])]
			  # send data to the client
		else:
			# store the data
			storage.append(data)
			msg = ('added to index ' + str(len(storage)))
		logging.info("from connected user: " + str(data))
		conn.send(msg.encode())

	conn.close()  # close the connection


if __name__ == '__main__':
	server_program()
