#!/usr/bin/env python

import os
import re
import sys
import glob
import math
import operator

# ----------------------------

from PIL import Image

def compare_images_pil(source, target):
	source_hist = Image.open(source).histogram()
	target_hist = Image.open(target).histogram()
	rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, source_hist, target_hist))/len(source_hist))
	return rms

# ----------------------------

from scipy.misc import imread
from scipy.linalg import norm
from scipy import sum, average

def _to_grayscale(arr):
	"""
	if arr is a color image (3D array), convert it to grayscale (2D array).
	"""
	result = average(arr, -1) if  len(arr.shape) == 3 else arr
	return result

def _normalize(arr):
	rng = arr.max()-arr.min()
	amin = arr.min()
	return (arr-amin)*255/rng

def compare_images_scipy(source, target):
	"""
	from http://stackoverflow.com/questions/189943/how-can-i-quantify-difference-between-two-images
	"""
	# read images as 2D arrays (convert to grayscale for simplicity)
	img_1 = _to_grayscale(imread(source).astype(float))
	img_2 = _to_grayscale(imread(target).astype(float))
	
	img_1 = _normalize(img_1)
	img_2 = _normalize(img_2)
	
	diff = img_1 - img_2  # elementwise for scipy arrays
	m_norm = sum(abs(diff))  # manhattan norm
	z_norm = norm(diff.ravel(), 0)  # zero norm
	return (m_norm, z_norm)

# ----------------------------

default_extentions = '.+(jpeg|png|gif|bmp|jpg)'

def _image_finder(current_path, extentions=default_extentions, initial_path=None, relative=True):
	current_path = current_path if current_path[-1] == '/' else (current_path + '/')
	initial_path = initial_path or current_path
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
	result = sorted(result)
	return result

def get_images(source_path, extentions=default_extentions, relative=True):
	result = _image_finder(source_path, extentions=extentions, relative=relative) if os.path.isdir(source_path) else ()
	return result

# ----------------------------

if __name__ == "__main__":
	s = get_images(sys.argv[1])
	print len(s)
	for x, p in enumerate(s):
		print p
		if x > 10: break
