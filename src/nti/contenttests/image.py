#!/usr/bin/env python

import sys
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

if __name__ == "__main__":
	source, target = sys.argv[1:1+2]
	print "PIL", compare_images_pil(source, target)
	print "scipy", compare_images_scipy(source, target)