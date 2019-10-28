
import socket
from threading import Thread 
# from SocketServer import ThreadingMixIn 

import logging
import psycopg2 

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

def connect_db():
	db_instance = psycopg2.connect(database='basic_values', user='postgres', password='password', host='127.0.0.1', port='5432')
	print('opened database')
	db_cursor = db_instance.cursor()
	return db_instance, db_cursor

def create_clean_table(db_instance, db_cursor):
	db_cursor.execute('DROP TABLE IF EXISTS numbers;')
	db_instance.commit()
	db_cursor.execute('CREATE TABLE IF NOT EXISTS numbers (row serial NOT NULL, input VARCHAR NOT NULL);')
	db_instance.commit()
	logging.info('Table created')


def get_row_from_db(row_number):
	db_instance, db_cursor = connect_db()
	try:
		db_cursor.execute('SELECT input FROM numbers WHERE row = %d;' % (row_number))
		rows = db_cursor.fetchall()
		print("ROWS", rows)	
		msg = ' '.join(rows[0])
	except:
		logging.warning('Row number %d for get request does not exist in table', row_number)	
		msg = 'Row does not exist'
	return msg	


# Multithreaded Python server : TCP Server Socket Thread Pool
class ClientThread(Thread): 
	def __init__(self,ip,port): 
		Thread.__init__(self) 
		self.ip = ip 
		self.port = port 
		print ("[+] New server socket thread started for " + ip + ":" + str(port))

	def run(self): 
		while True : 
			data = conn.recv(2048) 
			data = data.decode()
			print ("Server received data from client:", data)

			if data.split()[0] == 'get':
				try:
					row_number = int(data.split()[1])
				except:
					logging.warning('Get row_number %s does not exist', data.split()[1])
					MESSAGE = 'Invalid get request'
					conn.send(msg.encode())
					continue		
				MESSAGE = get_row_from_db(row_number)					
				conn.send(MESSAGE.encode())
			# if MESSAGE == 'exit':
			# 	break				
			# conn.send(MESSAGE.encode())  # echo 






class DeviceThread(Thread):
	def __init__(self,ip,port):
		Thread.__init__(self)
		self.ip = ip
		self.port = port
		print('New device thread started for ' + ip + ':' + str(port))
		self.db_instance, self.db_cursor = connect_db()
		create_clean_table(self.db_instance, self.db_cursor)

	def insert_into_db(self, data):
		self.data = data.decode()
		sql = 'INSERT INTO numbers (input) VALUES(%s);'
		print('data is' ,self.data)
		query = self.db_cursor.mogrify(sql, (self.data,))
		self.db_cursor.execute(query)
		self.db_instance.commit()
		msg = (self.data + ' added to index ')
		print("MSG IS ", msg)

	def run(self): 
		while True : 
			data = conn.recv(2048) 
			print ("Server received data from device:", data)
			self.insert_into_db(data)
			# MESSAGE = input("Multithreaded Python server : Enter Response from Server/Enter exit:")
			# if MESSAGE == 'exit':
				# break
			# conn.send(MESSAGE.encode())



# Multithreaded Python server : TCP Server Socket Program Stub
TCP_IP = '0.0.0.0' 
TCP_PORT = 2004 
BUFFER_SIZE = 20  # Usually 1024, but we need quick response 

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
tcpServer.bind((TCP_IP, TCP_PORT)) 
client_threads = [] 
device_threads = []

while True: 
	tcpServer.listen(4) 
	print ("Multithreaded Python server : Waiting for connections from TCP clients...")
	(conn, (ip,port)) = tcpServer.accept() 
	print('the ip and port are', ip, port)
	if not port == 55432:
		newthread = ClientThread(ip,port) 
		newthread.start() 
		client_threads.append(newthread)
	else:
		newthread = DeviceThread(ip, port)
		newthread.start()
		device_threads.append(newthread)

for t in threads: 
	t.join() 



# def socket_setup():
# 	host = socket.gethostname()
# 	dns_addr = socket.gethostbyname(host)
# 	port = 12345  # initiate port no above 1024
# 	server_socket = socket.socket()  # get instance
# 	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 	# look closely. The bind() function takes tuple as argument
# 	server_socket.bind((dns_addr, port))  # bind host address and port together

#     # configure how many client the server can listen simultaneously
# 	server_socket.listen(2)
# 	conn, address = server_socket.accept()  # accept new connection
# 	logging.info("Connection from: %s", address)
# 	return conn	

# def server_program():
# 	# get the hostname
# 	# host = socket.gethostname()
# 	# dns_addr = socket.gethostbyname(host)
# 	# port = 12345  # initiate port no above 1024

# 	conn = socket_setup()
# 	db_instance, db_cursor = connect_db()

# 	create_clean_table(db_instance, db_cursor)
	
# 	while True:
# 		# receive data stream. it won't accept data packet greater than 1024 bytes
# 		data = conn.recv(1024).decode()
# 		data = data.lower()
# 		if data.endswith('bye') or not data:
# 			break			
# 		elif data.split()[0] == 'get':
# 			# msg = storage[int(data.split()[1])]
# 			try:
# 				row_number = int(data.split()[1])
# 			except:
# 				logging.warning('Get row_number %s does not exist', data.split()[1])
# 				msg = 'Invalid get request'
# 				conn.send(msg.encode())
# 				continue
# 			try:
# 				db_cursor.execute('SELECT input FROM numbers WHERE row = %d;' % (row_number))
# 				rows = db_cursor.fetchall()
# 				print("ROWS", rows)	
# 				msg = ' '.join(rows[0])
# 			except:
# 				logging.warning('Row number %d for get request does not exist in table', row_number)	
# 				msg = 'Row does not exist'		
# 		else:
# 			sql = 'INSERT INTO numbers (input) VALUES(%s);'
# 			print(data)
# 			query = db_cursor.mogrify(sql, (data,))
# 			db_cursor.execute(query)
# 			db_instance.commit()
# 			msg = (data + ' added to index ')
# 		logging.info("from connected user: " + str(data))
# 		conn.send(msg.encode())

# 	conn.close()  # close the connection


# if __name__ == '__main__':
# 	server_program()
