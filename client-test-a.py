# Python TCP Client A
import socket 
import logging

host = socket.gethostname() 
port = 2004
BUFFER_SIZE = 20
MESSAGE = input("tcpClientA: Enter message/ Enter exit:") 

tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpClientA.bind((host, 12345))
tcpClientA.connect((host, port))

while MESSAGE != 'exit':
	tcpClientA.sendall(MESSAGE.encode())     
	data = tcpClientA.recv(BUFFER_SIZE)
	# tcpClientA.connect((host, port))
	print (" Client2 received data:", data)
	MESSAGE = input("tcpClientA: Enter message to continue/ Enter exit:")

tcpClientA.close()