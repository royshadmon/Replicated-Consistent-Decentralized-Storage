
# take in a single argument ex. bash start.sh 3
echo Input the number of servers
read noofservers
echo Creating $noofservers servers
# create/start 3 postgres instances
START=1

DBLOCATION=/Users/niharika/Desktop/Replicated-Consistent-Storage/server1
#DBLOGLOCATION=/Users/niharika/Desktop/Replicated-Consistent-Storage/servers/server1.log
declare -i PORT=5440
for (( c=$START; c<=$noofservers; c++ ))
do
	echo -n "$c "
	CURRENT="${DBLOCATION/1/$c}"
	echo "${CURRENT:0}"
	mkdir "${CURRENT:0}"
  initdb -D "${CURRENT:0}"
	LOGEXT=/server.log
	DBLOGLOCATION=$CURRENT$LOGEXT
	echo "${DBLOGLOCATION:0}"
	PORT+=1
	echo $PORT
	pg_ctl -D "${CURRENT:0}" -o "-p $((PORT))" -l "${DBLOGLOCATION:0}" start
	#dropdb "${CURRENT:0}"
done

# start 3 python3 servers each connecting to its own db instnace -p "$((PORT + 1))"

# script should run python3 device.py

# script should run python3 client.py
