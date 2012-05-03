#!/bin/bash

export TEST_WAIT=10
export PATH=/opt/local/bin:$PATH
export TMPDIR=/tmp
export TMPDIR=`mktemp -d -t nightly`
export DATASERVER_SYNC_CHANGES=True

WORKON_HOME=~/VirtualEnvs/
. ~/VirtualEnvs/nti.dataserver/bin/activate

LOG=~/tmp/lastNightlyTesting.txt

# checkout the source
svn up ~/Projects/NextThoughtPlatform > $LOG 2>&1

#  make sure all deps are upto date
cd ~/Projects/NextThoughtPlatform/nti.dataserver
python setup.py develop >> $LOG 2>&1

cd ~/Projects/NextThoughtPlatform/nti.integrationtests
python setup.py develop >> $LOG 2>&1

# Make change processing synchronous. If something fails,
# we know right away, and we don't have to wait for events

# let 'er rip!
date >> $LOG 2>&1

echo "Running general purpose tests" >> $LOG 2>&1
cd ~/Projects/NextThoughtPlatform/nti.integrationtests/src/nti/integrationtests/generalpurpose/utils
nosetests -s -d run_tests.py >> $LOG 2>&1

cd $TMPDIR

echo "Running integration tests" >> $LOG 2>&1
nti_run_integration_tests --use_coverage --sync_changes >> $LOG 2>&1

# combine coverage data from integration tests

coverage combine >> $LOG 2>&1

# move file to be combined later

if [ -f $TMPDIR/.coverage ]; then
	rm -f $TMPDIR/.coverage.int
	mv $TMPDIR/.coverage $TMPDIR/.coverage.int
fi

# change directory to run nose tests

cd ~/Projects/NextThoughtPlatform/nti.dataserver/src

# running nosetests

COVERDIR=${COVERDIR:-/Library/WebServer/Documents/cover-reports}
if [ -d $COVERDIR ]; then
	COVEROPT="--cover-html-dir=$COVERDIR"
fi

echo "Running nose tests" >> $LOG 2>&1
nosetests -d -e pywiki --with-coverage --cover-html $COVEROPT --cover-inclusive --cover-package=nti,socketio,geventwebsocket,wiktionary,context >> $LOG 2>&1

if [ -f .coverage ]; then
	rm -f $TMPDIR/.coverage.nose
	mv .coverage $TMPDIR/.coverage.nose
fi

# combine all results integration and nosetests

cd $TMPDIR
coverage combine >> $LOG 2>&1

# produce html report

if [ -d $COVERDIR ]; then
	coverage html -i --directory=$COVERDIR --omit="*/test/*,*/tests/*" >> $LOG 2>&1
fi

cat $LOG
if [ -d $COVERDIR ]; then
	cp $LOG $COVERDIR
fi

# Cleanup
cd ~
rm -rf $TMPDIR

