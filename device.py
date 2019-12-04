from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import time
import os
from datetime import datetime, timedelta
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
		data = []
		date = (datetime.now() + timedelta(seconds=value)).strftime('%Y-%m-%d %H:%M:%S')
		data.append((date, value))
		# data['input'] = value
		# data['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		tuples = [{'date':i[0], 'input': i[1]}  for i in data]
		# return str(data)
		return tuples


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

	while i < 100000:
		msg = create_message(i)
		print(str(msg))
		pubnub.publish().channel(device_channel).meta(meta).message(msg).sync()
		i+=1
		# time.sleep()


if __name__ == "__main__":    
	pubnub.add_listener(MySubscribeCallback())
	pubnub.subscribe().channels(device_channel).execute()
	main()