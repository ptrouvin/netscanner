#!/bin/bash

scriptdir=$(dirname $0)
piddir="$scriptdir/run"

usage() { 
	if [ -n "$1" ]; then
		echo "$1"
	fi
	cat - <<EOF 2>&1;
Usage: $0 [options] start|status|stop|restart [all|redis|flask]

default command=all

options:
-d     debug

EOF
	exit 1; 
}

DEBUG=''
TEST=''
FLASK_OPTIONS=""
while getopts ":d+t" o; do
    case "${o}" in
        d)
            DEBUG=1
			set -x
			;;
        t)
            TEST=1
			echo "TEST mode enabled"
			;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

status() {
	if [ -e $piddir/$1.pid ]; then
		pid=$(ps -p $(cat $piddir/$1.pid) 2>/dev/null | grep -v PID)
		if [ -n "$pid" ]; then
			echo "Process($1) $pid"
			return 0
		else
			echo "No process '$1'"
			rm -f $piddir/$1.pid
		fi
	else
		echo "MISSING $piddir/$1.pid"
	fi
	return 1
}

killproc() {
	pid=$(cat $piddir/$1.pid)
	if [ -n "$pid" ]; then
		echo "Kill($1) $pid"
		kill $pid
		rm -f $piddir/$1.pid
	else
		echo "No process '$1' to kill"
	fi
}

traite() {
	case "$1" in
		all)
			if [ $cmd = "start" ]; then
				traite redis
				sleep 1
				traite flask
			elif [ $cmd = "stop" ]; then
				traite flask
				traite redis
			elif [ $cmd = "status" ]; then
				traite redis
				traite flask
			fi
			;;
		redis)
			if [ $cmd = "start" ]; then
				rm -f dump.rdb; ~/Downloads/redis/redis-server.exe&
				pid=$!
				echo "$pid" > $piddir/redis-server.pid
			elif [ $cmd = "stop" ]; then
				killproc redis-server
			elif [ $cmd = "status" ]; then
				status redis-server
			fi
			;;
		flask)
			if [ $cmd = "start" ]; then
				python web.py -r '' -H 127.0.0.1 -b redis://localhost:6379 --log=info&
				pid=$!
				echo "$pid" > $piddir/web.pid
			elif [ $cmd = "stop" ]; then
				killproc web
			elif [ $cmd = "status" ]; then
				status web
			fi
			;;
	esac
}

command() {
	if [ -z "$1" ]; then
		traite all
	else
		while [ -n "$1" ]; do
			traite "$1"
			shift
		done
	fi
}

cmd="$1"
shift
case "$cmd" in
	start)
		echo "checking imap.config regarding mode.test->$TEST"
		if [ "$TEST" ]; then
			sed -ibak 's/"mode.test":false/"mode.test":true/' web.config
		else
			sed -ibak 's/"mode.test":true/"mode.test":false/' web.config
		fi
		command $*
		;;

	stop|status)
		command $*
		;;
	restart)
		cmd=stop
		command $*
		cmd=start
		command $*
		sleep 5
		cmd=status
		command $*
		;;
	*)
		usage "unknown command '$cmd'"
esac

