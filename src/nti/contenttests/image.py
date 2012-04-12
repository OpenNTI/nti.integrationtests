#!/usr/bin/env python

import os
import re
import sys
import glob
import math
import operator

from PIL import Image

import logging
logger = logging.getLogger( __name__ )
logging.basicConfig(level=logging.INFO,
					format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s')

default_extentions = '.+(jpeg|png|gif|bmp|jpg)'

# ----------------------------

def compare_images_pil(source, target):
	source_hist = Image.open(source).histogram()
	target_hist = Image.open(target).histogram()
	
	def f(a,b):
		a = a or 0
		b = b or 0
		return (a-b)**2
	
	rms = math.sqrt(reduce(operator.add, map(f, source_hist, target_hist))/len(source_hist))
	return rms

# ----------------------------

def _check_dir(path):
	path = path if path[-1] == '/' else (path + '/')
	return path

def _image_finder(current_path, extentions=default_extentions, initial_path=None, relative=True):
	current_path = _check_dir(current_path)
	initial_path = _check_dir(initial_path or current_path)
	result = set()
	for path in glob.iglob(current_path + '*'):
		if os.path.isdir(path):
			s = _image_finder(path, extentions, initial_path, relative)
			result.update(s)
		else:
			name = os.path.basename(path)
			if re.match(extentions, name):
				if relative:
					result.add(path[len(initial_path):])
				else:
					result.add(path)
	return result

def get_images(source_path, extentions=default_extentions, relative=True):
	result = _image_finder(source_path, extentions=extentions, relative=relative) if os.path.isdir(source_path) else ()
	return result

def compare_directories(source, target, out_file, extentions=default_extentions):
	out_file = os.path.expanduser(out_file)
	source = _check_dir(os.path.expanduser(source))
	target = _check_dir(os.path.expanduser(target))
	src_images = get_images(source, extentions=extentions)
	tgt_images = get_images(target, extentions=extentions)
	
	intersection = sorted(src_images.intersection(tgt_images))
	l_difference = sorted(src_images.difference(tgt_images))
	r_difference = sorted(tgt_images.difference(src_images))
	
	def _write(f, lst):
		f.write('\t'.join(lst))
		f.write('\n')
		f.flush()
		
	def _pil(src, tgt):
		try:
			return compare_images_pil(src, tgt)
		except:
			logger.exception("Error comparing '%s' and '%s'" % (src, tgt))
			return float('nan')
					
	with open(out_file, "w") as f:
		
		# header
		_write(f, ['name','master-size', 'target-size', 'histogram-comp'])
		
		# compare in both files
		for name in intersection:
			lst = []
			lst.append(name)
			src = os.path.join(source, name)
			lst.append(str(os.path.getsize(src)))
			tgt = os.path.join(target, name)
			lst.append(str(os.path.getsize(tgt)))
			
			pil = _pil(src, tgt)
			lst.append(str(pil))
			_write(f, lst)
			
		# only in source
		for name in l_difference:
			lst = []
			lst.append(name)
			src = os.path.join(source, name)
			lst.append(str(os.path.getsize(src)))
			_write(f, lst)
			
		# only in target
		for name in r_difference:
			lst = []
			lst.append(name)
			lst.append('')    # place holder for source target size
			tgt = os.path.join(target, name)
			lst.append(str(os.path.getsize(tgt)))
			_write(f, lst)
	
# ----------------------------

if __name__ == "__main__":
	src, tgt, out = sys.argv[1:4]
	compare_directories(src, tgt, out)
