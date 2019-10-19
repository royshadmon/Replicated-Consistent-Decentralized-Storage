
import socket


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
	server_socket.listen(1)
	conn, address = server_socket.accept()  # accept new connection
	print("Connection from: " + str(address))
	while True:
		# receive data stream. it won't accept data packet greater than 1024 bytes
		data = conn.recv(1024).decode()
		if not data:
			# if data is not received break
			break
		print("from connected user: " + str(data))
		msg = input(" -> ")
		conn.send(msg.encode())  # send data to the client

	conn.close()  # close the connection


if __name__ == '__main__':
	server_program()
