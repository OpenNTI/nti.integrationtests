import os
import nltk
from nltk.model import NgramModel
from nltk.probability import LidstoneProbDist

BUFFER = 6

class NLTKMessageGenerator:

	def __init__(self, filename, n = 3):
		with open(filename, "r") as f:
			raw = f.read()
			tokens = nltk.word_tokenize(raw)
			text = nltk.Text(tokens)
			estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
			self.trigram_model = NgramModel(n, text, estimator=estimator);
		
	def generate_message(self, length):
		ntext = self.trigram_model.generate(length + BUFFER)
		return ' '.join(ntext[BUFFER:length - 1])
	
	generate = generate_message
	
_default_message_generator = None
def default_message_generator():
	if not _default_message_generator:
		name = os.path.join(os.path.dirname(__name__), "DanielDeronda.txt");
		_default_message_generator = NLTKMessageGenerator(name)
	return _default_message_generator
