import os
import gzip
import threading


from nltk import Text
from nltk import word_tokenize
from nltk.model import NgramModel
from nltk.probability import LidstoneProbDist

BUFFER = 6

class NLTKMessageGenerator:

	def __init__(self, fileobj, n=3):
		raw = fileobj.read()
		tokens = word_tokenize(raw)
		text = Text(tokens)
		estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
		self.trigram_model = NgramModel(n, text, estimator=estimator);
		
	def generate_message(self, length):
		ntext = self.trigram_model.generate(length + BUFFER)
		return ' '.join(ntext[BUFFER:length - 1])
	
	generate = generate_message
	
_default_message_generator = None
lock = threading.Lock()

def default_message_generator():
	global _default_message_generator
	global lock
	with lock:
		if not _default_message_generator:
			name = os.path.join(os.path.dirname(__file__), "DanielDeronda.txt.gz");
			with gzip.open(name, "rb") as src:
				_default_message_generator = NLTKMessageGenerator(src)
			
	return _default_message_generator
