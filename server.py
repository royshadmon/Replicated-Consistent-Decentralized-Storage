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


pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-c-5f42fdef-c22f-4438-9650-27d1a37c22a7'
pnconfig.subscribe_key = 'sub-c-41b2ef2c-fc62-11e9-8f6e-d28065e14af1'
pnconfig.ssl = False
pubnub = PubNub(pnconfig)
pnconfig.filter_expression = "uuid !='" + pubnub.uuid +"'"
# pnconfig.filter_expression = "type !='" + my_type +"'"

db_instance = None
db_cursor = None

my_type = 'server'


device_channel = 'device_channel'
client_channel = 'client_channel'
meta_channel = 'meta_channel'
request_channel = 'request_channel'
recovery_channel = 'recovery_channel'
server_client_channel = 'server_client_%s_channel' % sys.argv[1]

messages_received = 0

log_file = None

# print('my UUID is', pubnub.uuid)


meta = {
    'uuid': pubnub.uuid,
    'type': my_type,
    'name': 'server1',
}

# logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

def connect_db(port_number):
    db_instance = psycopg2.connect(database='postgres', user='postgres', password='password', host='127.0.0.1',
                                   port=port_number)
    print('started database')
    db_cursor = db_instance.cursor()
    return db_instance, db_cursor


def setup(server_num):
    global log_file
    global db_instance
    global db_cursor
    log_file = ('server%s.log' % (server_num))
    print('logfile ', log_file)
    port_number = 5431 + int(server_num)
    db_instance, db_cursor = connect_db(port_number)
    
    # create_new_log_file()
    # create_clean_table(db_instance, db_cursor)
    
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels([device_channel, client_channel, request_channel, server_client_channel]).execute()
    


def create_clean_table(db_instance, db_cursor):
    db_cursor.execute('DROP TABLE IF EXISTS numbers;')
    db_instance.commit()
    db_cursor.execute('CREATE TABLE IF NOT EXISTS numbers (created_time timestamptz NOT NULL, input VARCHAR NOT NULL, PRIMARY KEY (created_time));')
    db_instance.commit()
    logging.info('Table created')

def create_new_log_file():
    if os.path.isfile(log_file):
        os.remove(log_file)
    myFile = open(log_file, 'w+')
    myFile.close()


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
            # msg = message.message.replace("\'", "\"")
            # res = json.loads(msg) 
            # print(message.user_metadata)
            process_recovered_data(message.message)
        elif message.channel == server_client_channel:            
            msg = get_row_from_db(message.message)
            send_message(msg, server_client_channel)
        elif message.channel == recovery_channel:

            # print(message.message)   
            print("IN HERE2")
            if not all(v is None for v in message.message):
                    process_recovered_data(message.message) 
                    
            pubnub.unsubscribe().channels(recovery_channel).execute()                     
            messages_received = 0
        elif message.channel == request_channel:
            print("IN HERE")
            rows = get_all_rows_since_timestamp(message.message)
            print("ROWS ARE ", rows)
            if not rows is None:
                data = []
                for row in rows:
                    data.append((row[0].strftime("%Y-%m-%d %H:%M:%S"), row[1]))
                tuples = [{'date':i[0], 'input': i[1]}  for i in data]
                print('sending data ', tuples)
                send_message(tuples, recovery_channel)
            else:
                send_message(None, recovery_channel)                



def insert_into_db(date, value):
    global db_instance
    global db_cursor
    sql = 'INSERT INTO numbers (created_time, input) VALUES(%s, %s) ON CONFLICT(created_time) DO NOTHING;'
    query = db_cursor.mogrify(sql, (date, value))
    print('query is %s' % query)
    db_cursor.execute(query)
    db_instance.commit()
    with open(log_file, 'a') as f:
        f.write(date + '\n')

def process_recovered_data(data):
    print('server 1 here ', data)
    
    if not all(v is None for v in data):
        for row in data:
            date = row['date']
            value = row['input']
            insert_into_db(date, value)

def send_message(msg, channel):
    global meta
    pubnub.publish().channel(channel).meta(meta).message(msg).pn_async(my_publish_callback)


def recover_at_startup():
    first_row = get_first_row_from_log()
    last_row = get_last_row_from_log()
    pubnub.subscribe().channels([recovery_channel]).execute()
    send_message([first_row, last_row], request_channel)


def get_first_row_from_log():
    try:
        with open(log_file, 'r') as f:
            row = f.readline().rstrip()
            if not row:
                return None
            return row
    except Exception as e:
        return None

def get_last_row_from_log():
    try:
        with open(log_file, 'r') as f:
            data = []
            data.append((list(f)[-1])) 
            return data[0].rstrip()
        # pubnub.publish().channel(recovery_channel).meta(meta).message(str(data)).sync()
    except Exception as e:
        return None

def get_row_from_db(date):
    global db_instance
    global db_cursor

    sql = 'SELECT input FROM numbers WHERE created_time = %s;'
    try:
        query = db_cursor.mogrify(sql, (date,))
        print("QUERY IS", query)
        db_cursor.execute(query)
        row = db_cursor.fetchone()
        if row:
            return ' '.join(row)
         
        return 'Date %s does not exist' % (date)
    except:
        logging.warning('Date %s for get request does not exist in table', date)
        msg = 'Date %s is not valid' % (date)
        return msg

def get_all_rows_since_timestamp(timestamp):
    global db_instance
    global db_cursor
    if timestamp[0] is None and timestamp[1] is None:
        sql = 'SELECT * FROM numbers;'
    else:
        sql = 'SELECT * FROM numbers WHERE created_time < %s OR created_time > %s;'
    try:
        query = db_cursor.mogrify(sql, (timestamp[0], timestamp[1]))
        print('query is %s' % query)

        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        if rows:
            return rows
         
        return None
    except:
        logging.warning('Timestamp %s is not valid' % (timestamp))
        msg = 'Timestamp %s is not valid' % (timestamp)
        return msg
 
# Run server indefinitely 
def main():
    while True:
        continue

if __name__ == "__main__": 
    global total_servers
    server_num = sys.argv[1] 
    
    setup(server_num)
    # send_message('hi', meta_channel)
    recover_at_startup()
    time.sleep(3)
    pubnub.unsubscribe().channels(recovery_channel).execute()                     


