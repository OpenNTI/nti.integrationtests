#!/bin/bash

export PATH=/opt/local/bin:$PATH
export TMPDIR=/tmp
CHECKOUT_DIR=`mktemp -d -t nightly`
cd $CHECKOUT_DIR

# checkout the source

svn co -q https://svn.nextthought.com/repository/AoPS/trunk AoPS
svn co -q https://svn.nextthought.com/repository/NextThoughtPlatform/trunk/ NextThoughtPlatform

# install the dictionary file

TEST_DIR=`pwd`/NextThoughtPlatform/src/test/python
PYTHONPATH=`pwd`/NextThoughtPlatform/src/main/python
mkdir -p $PYTHONPATH/wiktionary/
cp ~/bin/dict.db $PYTHONPATH/wiktionary/

# setup a location for the dataserver

mkdir Data
export DATASERVER_DIR=`pwd`/Data
export TEST_WAIT=10
# Make change processing synchronous. If something fails,
# we know right away, and we don't have to wait for events
export DATASERVER_SYNC_CHANGES=True
#export DATASERVER_NO_REDIRECT=1
LOG=~/tmp/lastNightlyTesting.txt
export PATH=/opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin:$PATH

mkdir -p $DATASERVER_DIR

function kill_python_procs()
{
	user_id=`whoami`
	proc_id='Python'
	for p in `ps -u ${user_id} | grep '/*/'${proc_id} | grep -v grep | awk '{print $2}'` 
	do
		echo "killing ${p}"
 		kill -9 ${p} 
	done
}

function stop_daemons()
{
	for i in $1/*.zconf.xml; do
		zdaemon -C $i stop
	done
}

function clean_data()
{
	rm -rf $1
	mkdir -p $1
}

# let 'er rip!
date
export PYTHONPATH

python2.7 $TEST_DIR/ServerTest_v2.py > $LOG 2>&1
stop_daemons $DATASERVER_DIR
clean_data $DATASERVER_DIR

python2.7 $TEST_DIR/ServerTest_v3_quizzes.py >> $LOG 2>&1
stop_daemons $DATASERVER_DIR
clean_data $DATASERVER_DIR

# kill_python_procs
python2.7 $TEST_DIR/run_integration_tests.py --use_coverage >> $LOG 2>&1
stop_daemons $DATASERVER_DIR
clean_data $DATASERVER_DIR

# combine coverage data from integration tests

coverage combine

# move file to be combined later

if [ -f $CHECKOUT_DIR/.coverage ]
then
	mv $CHECKOUT_DIR/.coverage $PYTHONPATH/.coverage.int
fi

# change directory to run nose tests

cd $PYTHONPATH

# running nosetests

COVERDIR=${COVERDIR:-/Library/WebServer/Documents/cover-reports}
if [ -d $COVERDIR ]; then
	COVEROPT="--cover-html-dir=$COVERDIR"
fi

nosetests -d -e pywiki --with-coverage --cover-html $COVEROPT --cover-inclusive --cover-package=nti,socketio,geventwebsocket,wiktionary,context >> $LOG 2>&1

if [ -f $PYTHONPATH/.coverage ]
then
	mv $PYTHONPATH/.coverage $PYTHONPATH/.coverage.nose
fi

# combine all results integration and nosetests

coverage combine

# produce html report

if [ -d $COVERDIR ]; then
	coverage html -i --directory=$COVERDIR --omit="*/test/*,*/tests/*"
fi

stop_daemons $DATASERVER_DIR
cat $LOG
if [ -d $COVERDIR ]; then
	cp $LOG $COVERDIR
fi

# Cleanup
cd ~
rm -rf $CHECKOUT_DIR
date
