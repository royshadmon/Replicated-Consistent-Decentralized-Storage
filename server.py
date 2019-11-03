
import socket
from threading import Thread
import threading 

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
					conn.sendall(msg.encode())
					continue		
				MESSAGE = get_row_from_db(row_number)					
				conn.sendall(MESSAGE.encode())
				print("MESSAGE SENT")			
			# if MESSAGE == 'exit':
			# 	break				
			# conn.send(MESSAGE.encode())  # echo 





class DeviceThread(Thread):
	def __init__(self,ip,port, didExist):
		Thread.__init__(self)
		self.ip = ip
		self.port = port
		print('New device thread started for ' + ip + ':' + str(port))
		self.db_instance, self.db_cursor = connect_db()
		if not didExist:
			print("DIDEXIST 1", didExist)
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
			try:
				data = conn.recv(2048) 
			except Exception as e:
				print('Error is')
				continue
			print ("Server received data from device:", data)
			self.insert_into_db(data)

			# MESSAGE = input("Multithreaded Python server : Enter Response from Server/Enter exit:")
			# if MESSAGE == 'exit':
				# break
			# conn.send(MESSAGE.encode())



# Multithreaded Python server : TCP Server Socket Program Stub
# TCP_IP = '0.0.0.0' 
TCP_IP = socket.gethostname() 
TCP_PORT = 2004 
BUFFER_SIZE = 20  # Usually 1024, but we need quick response 

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
tcpServer.bind((TCP_IP, TCP_PORT)) 

client_threads = {} 
device_threads = {}


didExist = False
while True: 
	tcpServer.listen(10) #infinity loop
	print ("Multithreaded Python server : Waiting for connections from TCP clients...")
	(conn, (ip,port)) = tcpServer.accept() 
	print('the ip and port are', ip, port)
	if not port == 55432:
		newthread = ClientThread(ip,port) 
		newthread.start() 
		print("CLIENT thread started")
		client_threads[port] = newthread
	else:
		if port in device_threads:
			device_threads.pop(port)
			didExist = True
		newthread = DeviceThread(ip, port, didExist)
		didExist = False
		device_threads[port] = newthread
		newthread.start()	
		print("DEVICE thread started")		
		



