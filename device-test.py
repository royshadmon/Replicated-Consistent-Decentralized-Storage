# Python TCP Client B
import socket 
import time
import logging

host = socket.gethostname() 
port = 2004
BUFFER_SIZE = 20
MESSAGE = input("tcpClientB: Enter message/ Enter exit:")



def connect_to_server():
	tcpClientB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# allows you to immediately restart TCP server
	# tcpClientB.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# set device to port 55432
	tcpClientB.bind((host, 55432))
	print(tcpClientB) 
	tcpClientB.connect((host, port))
	return tcpClientB

def restart_socket(tcpClientB):
	tcpClientB.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	tcpClientB.bind((host, 55432))
	tcpClientB.connect((host, port))
	return tcpClientB

i = 1000
tcpClientB = connect_to_server()
while MESSAGE != 'exit':
	try:
		i = i+1
		MESSAGE = str(i)
		tcpClientB.sendall(MESSAGE.encode())     
	except Exception as e:
		logging.warning('Oh no theres an Error %s', e)
		tcpClientB.close()
		tcpClientB = connect_to_server()
	# data = tcpClientB.recv(BUFFER_SIZE)
	# print (" Client received data:", data)
	# MESSAGE = input("tcpClientB: Enter message to continue/ Enter exit:")
	time.sleep(3)
	

tcpClientB.close()