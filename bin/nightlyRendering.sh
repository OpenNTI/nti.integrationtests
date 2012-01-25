#!/bin/bash
. ~/bin/dataserver_vars.sh
export PATH=/opt/local/bin:$PATH
export TMPDIR=/tmp
CHECKOUT_DIR=`mktemp -d -t nightly`
cd $CHECKOUT_DIR
echo $CHECKOUT_DIR

# checkout the source
# We use the existing virtual environment, updated on its own schedule

svn co -q https://svn.nextthought.com/repository/AoPSBooks/ AoPSBooks

# let 'er rip!
date

cd AoPSBooks
./gen-images.sh
cd Prealgebra_text/
nti_render prealgebra.tex xhtml

gcp -dpR prealgebra/* /Library/WebServer/Documents/prealgebra/

# Cleanup
cd ~
rm -rf $CHECKOUT_DIR
date
