
# take in a single argument ex. bash start.sh 3
echo Input the number of servers
read noofservers
echo Creating $noofservers servers
# create/start 3 postgres instances
START=1
DBLOCATION= "/Users/niharika/Library/Application\Support/Postgres"
DBLOGLOCATION= "/Users/niharika/Library/ApplicationSupport/Postgres/postgresql.log"
PORT=5435
for (( c=$START; c<=$noofservers; c++ ))
do
	echo -n "$c "

	initdb -D /Users/niharika/Library/Application\Support/Postgres
	echo "here"
	echo "pg_ctl -D $DBLOCATION -o $PORT -l $DBLOGLOCATION start"
	pg_ctl -D $DBLOCATION -o "$((PORT + 1))" -l $DBLOGLOCATION start
	#pg_ctl -D /Users/niharika/Library/ApplicationSupport/Postgres -o "-p 5435" -l /Users/niharika/Library/ApplicationSupport/Postgres/postgresql.log stop
done
echo
# start 3 python3 servers each connecting to its own db instnace

# script should run python3 device.py

# script should run python3 client.py
