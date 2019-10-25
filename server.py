
import socket
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

def socket_setup():
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
	return conn	

def server_program():
	# get the hostname
	# host = socket.gethostname()
	# dns_addr = socket.gethostbyname(host)
	# port = 12345  # initiate port no above 1024

	conn = socket_setup()
	db_instance, db_cursor = connect_db()

	create_clean_table(db_instance, db_cursor)
	
	
	# server_socket = socket.socket()  # get instance
	# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# # look closely. The bind() function takes tuple as argument
	# server_socket.bind((dns_addr, port))  # bind host address and port together

 #    # configure how many client the server can listen simultaneously
	# server_socket.listen(2)
	# conn, address = server_socket.accept()  # accept new connection
	# logging.info("Connection from: %s", address)
	while True:
		# receive data stream. it won't accept data packet greater than 1024 bytes
		data = conn.recv(1024).decode()
		data = data.lower()
		if data.endswith('bye') or not data:
			break			
		elif data.split()[0] == 'get':
			# msg = storage[int(data.split()[1])]
			try:
				row_number = int(data.split()[1])
			except:
				logging.warning('Get row_number %s does not exist', data.split()[1])
				msg = 'Invalid get request'
				conn.send(msg.encode())
				continue
			try:
				db_cursor.execute('SELECT input FROM numbers WHERE row = %d;' % (row_number))
				rows = db_cursor.fetchall()
				print("ROWS", rows)	
				msg = ' '.join(rows[0])
			except:
				logging.warning('Row number %d for get request does not exist in table', row_number)	
				msg = 'Row does not exist'		
		else:
			sql = 'INSERT INTO numbers (input) VALUES(%s);'
			print(data)
			query = db_cursor.mogrify(sql, (data,))
			db_cursor.execute(query)
			db_instance.commit()
			msg = (data + ' added to index ')
		logging.info("from connected user: " + str(data))
		conn.send(msg.encode())

	conn.close()  # close the connection


if __name__ == '__main__':
	server_program()
