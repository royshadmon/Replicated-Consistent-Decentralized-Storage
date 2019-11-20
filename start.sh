
# take in a single argument ex. bash start.sh 3
echo Input the number of servers
read noofservers
echo Creating $noofservers servers
# create/start 3 postgres instances
START=1
#END=5
for (( c=$START; c<=$noofservers; c++ ))
do
	echo -n "$c "
done
echo
# start 3 python3 servers each connecting to its own db instnace

# automation of server->server (many-to-many)

# script should run python3 device.py

# script should run python3 client.py
