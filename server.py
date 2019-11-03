from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import time
import os
import logging
import psycopg2

# logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-c-5f42fdef-c22f-4438-9650-27d1a37c22a7'
pnconfig.subscribe_key = 'sub-c-41b2ef2c-fc62-11e9-8f6e-d28065e14af1'
pnconfig.ssl = False
pubnub = PubNub(pnconfig)
pnconfig.filter_expression = "uuid !='" + pubnub.uuid +"'"

db_instance = None
db_cursor = None

device_channel = 'device_channel'
client_channel = 'client_channel'
user_id = 1

# class Msg:
#     def __init__(self, msg):
#         self.user_id = user_id
#         self.msg = msg

meta = {
    'uuid': pubnub.uuid,
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
    db_cursor.execute('CREATE TABLE IF NOT EXISTS numbers (row serial NOT NULL, input VARCHAR NOT NULL);')
    db_instance.commit()
    logging.info('Table created')


def insert_into_db(data):
    global db_instance
    global db_cursor
    # data = data.decode()
    sql = 'INSERT INTO numbers (input) VALUES(%s);'
    print('data is', data)
    query = db_cursor.mogrify(sql, (data,))
    db_cursor.execute(query)
    db_instance.commit()
    msg = (data + ' added to index ')
    print("MSG IS ", msg)


def get_row_from_db(row_number):
    # db_instance, db_cursor = connect_db()
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
        print("from device 2: " + message.message)
        print(message.channel)
        if message.channel == device_channel:
            insert_into_db(message.message)
        else:
            # msg = Msg(get_row_from_db(message.message))
            msg = get_row_from_db(message.message)
            # print('send client msg %s %s\n' % (msg.msg, msg.user_id))
            send_message(msg)

def send_message(msg):
    print('the message sent is %s' % msg)
    # pubnub.publish().channel(client_channel).message(str(msg)).pn_async(my_publish_callback)                  
    pubnub.publish().channel(client_channel).meta(meta).message(msg).sync()



## publish a message
def main():
    while True:
        continue
        # msg = input("Input a message to publish: ")
        # if msg == 'exit': os._exit(1)
        # pubnub.publish().channel(client_channel).message(str(msg)).pn_async(my_publish_callback)

if __name__ == "__main__":    
    db_instance, db_cursor = connect_db()
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels([device_channel, client_channel]).execute()
    create_clean_table(db_instance, db_cursor)
    # pubnub.subscribe().channels(client_channel).execute()
    main()

