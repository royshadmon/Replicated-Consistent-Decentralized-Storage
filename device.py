from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import time
import os
from datetime import datetime
import json

pnconfig = PNConfiguration()

pnconfig.publish_key = 'pub-c-5f42fdef-c22f-4438-9650-27d1a37c22a7'
pnconfig.subscribe_key = 'sub-c-41b2ef2c-fc62-11e9-8f6e-d28065e14af1'
pnconfig.ssl = False

pubnub = PubNub(pnconfig)
pnconfig.filter_expression = "uuid !='" + pubnub.uuid +"'"

device_channel = 'device_channel'

meta = {
    'uuid': pubnub.uuid,
    'type': 'device',
}

def create_message(value):
		data = {}
		data['value'] = value
		data['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7]
		return str(data)


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
		print("from server message: " + message.message)



## publish a message

def main():
	i = 0
	while True:
		msg = create_message(i)
		print(str(msg))
		pubnub.publish().channel(device_channel).meta(meta).message((msg)).pn_async(my_publish_callback)
		i+=1
		time.sleep(3)


if __name__ == "__main__":    
	pubnub.add_listener(MySubscribeCallback())
	pubnub.subscribe().channels(device_channel).execute()
	main()