# Replicated-Consistent-Storage

## Build instructions for 1 client, 1 device, 3 servers

1. Start 3 postgres instances on port 5432, 5433, 5434.
2. Install dependencies:
```
pip3 install psycog2-binary
pip3 install pubnub
```
3. Start devices in individual terminals:
```
python3 server.py 1
python3 server.py 2
python3 server.py 3
python3 client.py 3
python3 device.py
```

You should notice servers beginning to accept data. 

## Instructions to run a lookup

In the client terminal run the following query:
```
[device number] [date]
```
Example lookup on device 2:
```
2 2019-12-03 18:59:15 
```

## Test fault-tolerance
1. Kill one of the servers.
2. Restart one of the servers.
3. Start the device so that additional data is inserted into the other devices. 
4. Start the server that was killed.  
5. Validate that the restarted server recorded the missed data. 
