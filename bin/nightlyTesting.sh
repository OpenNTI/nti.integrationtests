#!/bin/bash

. ~/bin/dataserver_vars.sh
export PATH=/opt/local/bin:$PATH
export TMPDIR=/tmp
CHECKOUT_DIR=`mktemp -d -t nightly`
cd $CHECKOUT_DIR

# checkout the source
svn up ~/Projects/NextThoughtPlatform

#  make sure all deps are upto date
python ~/Projects/NextThoughtPlatform/nti.dataserver/setup.py develop
python ~/Projects/NextThoughtPlatform/nti.integrationtests/setup.py develop

# setup a location for the dataserver

mkdir Data
export DATASERVER_DIR=`pwd`/Data
export TEST_WAIT=10

# Make change processing synchronous. If something fails,
# we know right away, and we don't have to wait for events

export DATASERVER_SYNC_CHANGES=True
LOG=~/tmp/lastNightlyTesting.txt

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

python ServerTest_v2.py > $LOG 2>&1
#stop_daemons $DATASERVER_DIR
#clean_data $DATASERVER_DIR

#python $TEST_DIR/ServerTest_v3_quizzes.py >> $LOG 2>&1
#stop_daemons $DATASERVER_DIR
#clean_data $DATASERVER_DIR

#python $TEST_DIR/run_integration_tests.py --use_coverage >> $LOG 2>&1
#stop_daemons $DATASERVER_DIR
#clean_data $DATASERVER_DIR

# combine coverage data from integration tests

#coverage combine

# move file to be combined later

#if [ -f $CHECKOUT_DIR/.coverage ]; then
#	mv $CHECKOUT_DIR/.coverage $PYTHONPATH/.coverage.int
#fi

# change directory to run nose tests

#cd $PYTHONPATH
cd ~/Projects/NextThoughtPlatform/nti.dataserver/src
# running nosetests

COVERDIR=${COVERDIR:-/Library/WebServer/Documents/cover-reports}
if [ -d $COVERDIR ]; then
	COVEROPT="--cover-html-dir=$COVERDIR"
fi

nosetests -d -e pywiki --with-coverage --cover-html $COVEROPT --cover-inclusive --cover-package=nti,socketio,geventwebsocket,wiktionary,context >> $LOG 2>&1

if [ -f $PYTHONPATH/.coverage ]; then
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
