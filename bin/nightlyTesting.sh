#!/bin/bash

export PATH=/opt/local/bin:$PATH
export TMPDIR=/tmp
CHECKOUT_DIR=`mktemp -d -t nightly`
cd $CHECKOUT_DIR

WORKON_HOME=~/VirtualEnvs/
. ~/VirtualEnvs/nti.dataserver/bin/activate

# checkout the source
svn up ~/Projects/NextThoughtPlatform

#  make sure all deps are upto date
cd ~/Projects/NextThoughtPlatform/nti.dataserver
python setup.py develop

cd ~/Projects/NextThoughtPlatform/nti.integrationtests
python setup.py develop

# setup a location for the dataserver

cd $CHECKOUT_DIR
mkdir Data
export DATASERVER_DIR=`pwd`/Data
export TEST_WAIT=10

# Make change processing synchronous. If something fails,
# we know right away, and we don't have to wait for events

export DATASERVER_SYNC_CHANGES=True
LOG=~/tmp/lastNightlyTesting.txt

function clean_data()
{
	rm -rf $1
	mkdir -p $1
}

# let 'er rip!
date

echo "Running legacy version tests"
run_legacy_v2_tests > $LOG 2>&1
clean_data $DATASERVER_DIR

echo "Running legacy version tests quizzes"
run_legacy_v3_tests > $LOG 2>&1
clean_data $DATASERVER_DIR

echo "Running integration tests"
run_integration_tests --use_coverage >> $LOG 2>&1
clean_data $DATASERVER_DIR

# combine coverage data from integration tests

coverage combine

# move file to be combined later

if [ -f $CHECKOUT_DIR/.coverage ]; then
	rm -f $TMPDIR/.coverage.int
	mv $CHECKOUT_DIR/.coverage $TMPDIR/.coverage.int
fi

# change directory to run nose tests

cd ~/Projects/NextThoughtPlatform/nti.dataserver/src

# running nosetests

COVERDIR=${COVERDIR:-/Library/WebServer/Documents/cover-reports}
if [ -d $COVERDIR ]; then
	COVEROPT="--cover-html-dir=$COVERDIR"
fi

echo "Running nose tests"
nosetests -d -e pywiki --with-coverage --cover-html $COVEROPT --cover-inclusive --cover-package=nti,socketio,geventwebsocket,wiktionary,context >> $LOG 2>&1

if [ -f .coverage ]; then
	rm -f $TMPDIR/.coverage.nose
	mv .coverage $TMPDIR/.coverage.nose
fi

# combine all results integration and nosetests

cd $TMPDIR/
coverage combine

# produce html report

if [ -d $COVERDIR ]; then
	coverage html -i --directory=$COVERDIR --omit="*/test/*,*/tests/*"
fi

cat $LOG
if [ -d $COVERDIR ]; then
	cp $LOG $COVERDIR
fi

# Cleanup
cd ~
rm -rf $CHECKOUT_DIR
date
