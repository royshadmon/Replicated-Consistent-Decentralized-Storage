from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import time
import os
import sys

pnconfig = PNConfiguration()

pnconfig.publish_key = 'pub-c-5f42fdef-c22f-4438-9650-27d1a37c22a7'
pnconfig.subscribe_key = 'sub-c-41b2ef2c-fc62-11e9-8f6e-d28065e14af1'
pnconfig.ssl = False

pubnub = PubNub(pnconfig)

# pubnub.add_listener(MySubscribeCallback())
# pubnub.subscribe().channels(client_channel).execute()

channels = []
meta = {
    'uuid': pubnub.uuid,
    'type': 'client',
}

def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        print('Presence ', presence)
        pass

    def status(self, pubnub, status):
        pass

    def message(self, pubnub, message):
        # print("from server: " + message.message)
        print(message.message)



## publish a message
def main():
    global channels
    while True:
        msg = input("Input a message to publish: ")
        if msg == 'exit': os._exit(1)
        msg = msg.split(' ', 1)
        try:
            channel = 'server_client_%s_channel' % msg[0]
        except Exception as e:
            print('Please direct a request to one of the following channels by listing just the number associated to that channel %s' % channels)
            continue
        if channel in channels:
            pubnub.publish().channel(channel).meta(meta).message(msg[1]).pn_async(my_publish_callback)
        else:
            print('Channel does not exist. Please try again')

if __name__ == "__main__":    
    total_servers = int(sys.argv[1])
    channels = []
    for i in range(1, total_servers + 1):
        server_client_channel = 'server_client_%d_channel' % i
        channels.append(server_client_channel)
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(channels).execute()
    main()