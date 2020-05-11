while true
do
    python3 Updater.py
    if [ -f pid ]
    then
        kill `cat pid`
    fi
    python3 app.py $HOST $PORT &
    echo $! >pid
    sleep $INTVL


done



