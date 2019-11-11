from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import time
import os
import logging
import psycopg2
import json
import sys
from datetime import datetime


my_type = 'server'
# logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

server_name = 'server1.log'

pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-c-5f42fdef-c22f-4438-9650-27d1a37c22a7'
pnconfig.subscribe_key = 'sub-c-41b2ef2c-fc62-11e9-8f6e-d28065e14af1'
pnconfig.ssl = False
pubnub = PubNub(pnconfig)
pnconfig.filter_expression = "uuid !='" + pubnub.uuid +"'"
# pnconfig.filter_expression = "type !='" + my_type +"'"

db_instance = None
db_cursor = None

recovery_channel = 'recovery_channel'
device_channel = 'device_channel'
client_channel = 'client_channel'

print('my UUID is', pubnub.uuid)

meta = {
    'uuid': pubnub.uuid,
    'type': my_type,
}

def connect_db():
    db_instance = psycopg2.connect(database='postgres', user='postgres', password='password', host='127.0.0.1',
                                   port='5432')
    print('opened database')
    db_cursor = db_instance.cursor()
    return db_instance, db_cursor


def create_clean_table(db_instance, db_cursor):
    db_cursor.execute('DROP TABLE IF EXISTS numbers;')
    db_instance.commit()
    db_cursor.execute('CREATE TABLE IF NOT EXISTS numbers (created_time timestamptz NOT NULL, input VARCHAR NOT NULL, row serial NOT NULL);')
    db_instance.commit()
    logging.info('Table created')


def insert_into_db(data):
    global db_instance
    global db_cursor
    sql = 'INSERT INTO numbers (created_time, input) VALUES(%s, %s);'
    query = db_cursor.mogrify(sql, (data['datetime'], data['value']))
    db_cursor.execute(query)
    db_instance.commit()
    msg = (data['datetime'] + ' and ' + str(data['value']) + ' added to index ')
    with open(server_name, 'a') as f:
        f.write(data['datetime'] + '\n')
    print('success')

def get_row_from_db(row_number):
    global db_instance
    global db_cursor
    try:
        db_cursor.execute('SELECT input FROM numbers WHERE row = %d;' % (int(row_number)))
        rows = db_cursor.fetchall()
        if rows:
            return ' '.join(rows[0])
         
        return 'Row %s does not exist' % (row_number)
    except:
        logging.warning('Row number %d for get request does not exist in table', row_number)
        msg = 'Row %s is not valid' % (row_number)
        return msg


def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass

    def status(self, pubnub, status):
        pass

    def message(self, pubnub, message):
        if message.channel == device_channel:
            msg = message.message.replace("\'", "\"")
            res = json.loads(msg) 
            insert_into_db(res)
        elif message.channel == client_channel:            
            msg = get_row_from_db(message.message)
            send_message(msg)
        elif message.channel == recovery_channel:
            print(message.channel)
            # recovery()  
            # last_row = get_row_from_db()
            rows = get_all_rows_since_timestamp(message.message)
            data = []
            for row in rows:
                data.append((row[0].strftime("%Y-%m-%d %H:%M:%S"), row[1], row[2]))
                # row[0] = row[0].strftime("%Y-%m-%d %H:%M:%S")
            tuples = [{'date':i[0], 'input': i[1], 'row': i[2]}  for i in data]
            print('sending data ', tuples)
            # for row in tuples:
            #     print(sys.getsizeof(row))
            pubnub.publish().channel(recovery_channel).meta(meta).message(tuples).sync()


def send_message(msg):
    print('the message sent is %s' % msg)
    pubnub.publish().channel(client_channel).meta(meta).message(msg).sync()


def get_last_row_from_log():
    try:
        with open(server_name, 'r') as f:
            data = []
            data.append((list(f)[-1])) 
            return data[0].replace('\n', '')
        # pubnub.publish().channel(recovery_channel).meta(meta).message(str(data)).sync()
    except Exception as e:
        return None

def get_all_rows_since_timestamp(timestamp):
    global db_instance
    global db_cursor
    try:
        query = 'SELECT * FROM numbers WHERE created_time > \'%s\';' % (timestamp)
        print(query)
        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        if rows:
            return rows
         
        return '%s Is the most up-to-date' % (timestamp)
    except:
        logging.warning('Timestamp %s is not valid' % (timestamp))
        msg = 'Timestamp %s is not valid' % (timestamp)
        return msg
 
# Run server indefinitely 
def main():
    while True:
        continue

if __name__ == "__main__":    
    db_instance, db_cursor = connect_db()
    # timestamp = get_last_row_from_log()
    # rows = get_all_rows_since_timestamp(timestamp)
    # for row in rows:
    #     print(row[0].strftime("%Y-%m-%d %H:%M:%S") + ' %s %d' % (row[1], row[2]))
    # exit()
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels([device_channel, client_channel, recovery_channel]).execute()
    create_clean_table(db_instance, db_cursor)
    # pubnub.subscribe().channels(client_channel).execute()
    main()

