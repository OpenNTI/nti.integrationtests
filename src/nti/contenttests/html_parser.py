import os
import sys
import lxml.html as lhtml

from nltk import clean_html

# ----------- object classes ------------

class Meta(object):
	
	def __init__(self, name, content):
		self.name = name
		self.content = content
	
	def __eq__(self, other):
		return self.name == other.name and self.content == other.content
	
	def __str__(self):
		return '(%s, %s)' % (self.name, self.content)
	
class Link(object):
	
	def __init__(self, title, href, rel):
		self.rel = rel
		self.href = href
		self.title = title
	
	def __eq__(self, other):
		return  self.href == other.href and \
				self.rel == other.rel and \
				self.title == other.title

	def __str__(self):
		return '(%s, %s, %s)' % (self.title, self.rel, self.title)
	
class Span(object):
	
	def __init__(self, text):
		self.text = text
	
	def __eq__(self, other):
		return self.text == other.text
	
	def __str__(self):
		return '(%s)' % self.text
	
class Anchor(object):
	
	def __init__(self, name, Id):
		self.name = name
		self.Id = Id
	
	def __eq__(self, other):
		return self.name == other.name and self.Id == other.Id
	
	def __str__(self):
		return '(%s, %s)' % (self.name, self.Id)
	
class Image(object):
	
	def __init__(self, style):
		self.style = style
	
	def __eq__(self, other):
		return self.style == other.style

	def __str__(self):
		return '(%s)' % self.style
	
class IFrame(object):
	
	def __init__(self, src):
		self.src = src
	
	def __eq__(self, other):
		return self.src == other.src
	
	def __str__(self):
		return '(%s)' % self.src
	
class Paragraph(object):
	
	def __init__(self, name, text):
		self.name = name
		self.text = clean_html(text)
	
	def __eq__(self, other):
		return self.name == other.name and self.text == other.text
	
	def __str__(self):
		return '(%s, %s)' % (self.name, self.text)

# ------------ object collections ----------

class ElementsCollection(object):
	
	def add_element(self, info):
		self.data.append(info)
		
	def add_value(self, key, value):
		self.data[key] = value
	
	def __len__(self):
		return len(self.data)

class MetaCollection(ElementsCollection):
	
	def __init__(self):
		self.data = {}
		self.data['content'] = None

class LinksCollection(ElementsCollection):
	
	def __init__(self):
		self.data = {}
		
class SpanCollection(ElementsCollection):
	
	def __init__(self):
		self.data = {}
		self.data['ref'] = None
		self.data['label'] = None

class AnchorCollection(ElementsCollection):
	
	def __init__(self):
		self.data = []
		
class ImageCollection(ElementsCollection):
	
	def __init__(self):
		self.data = []
		
class IFrameCollection(ElementsCollection):
	
	def __init__(self):
		self.data = []
		
IframeCollection = IFrameCollection

class ParagraphCollection(ElementsCollection):
	
	def __init__(self):
		self.data = []

# ------------ add data to collections -------------

_html_data_keys = ('meta', 'links', 'span', 'anchor', 'image', 'iframe', 'paragraph')
_html_elements =  ('meta', 'link', 'span', 'a', 'image', 'iframe', 'p')

class HtmlData(object):
	
	def __init__(self, doc):
		self.doc = doc
		g = globals()
		self.parsed_html = {}
		for key in _html_data_keys:
			cname = "%sCollection" % key.capitalize()
			self.parsed_html[key] = g[cname]()
	
	@property
	def links(self):
		return self.parsed_html['links']
	
	@property
	def span(self):
		return self.parsed_html['span']
		
	@property
	def meta(self):
		return self.parsed_html['meta']
	
	# ---------
	
	def parse_links(self, elem):
		rel = elem.get('rel')
		if rel in ('next', 'prev', 'up'):
			self.links.add_value(rel, Link(elem.get("title"), elem.get("href"), rel))		
			
	def parse_meta(self, elem):
		name = elem.get("name")
		if name == 'NTIID':
			self.meta.add_value(name, Meta(name, elem.get('content')))

	def parse_span(self, elem):
		clazz = elem.get('class')
		if clazz in ('ref', 'label'):
			self.span.add_value(clazz, Span(self.to_text(elem)))

	def parse_anchor(self, elem):
		self.parsed_html['anchor'].add_element(Anchor(elem.get("name"), elem.get("id")))

	def parse_image(self, elem):
		self.parsed_html['image'].add_element(Image(elem.get("style")))
	
	def parse_iframe(self, elem):
		self.parsed_html['iframe'].add_element(IFrame(elem.get("src")))
	
	def parse_paragraph(self, elem):
		self.parsed_html['paragraph'].add_element(Paragraph(elem.get("name"), self.to_text(elem)))
	
	def to_text(self, elem):
		ret = []
		ret.append(elem.text or "")
		for child in elem.getchildren():
			ret.append(self.to_text(child))
			ret.append(child.tail or "")
		return ''.join(ret)
	
	@classmethod
	def parse_element(cls, parser, elem):
		tag = elem.tag
		if tag in _html_elements:
			idx = _html_elements.index(tag)
			name = 'parse_%s' % _html_data_keys[idx]
			method = getattr(parser, name)
			method(elem) 
			
		for child in elem.getchildren():
			HtmlData.parse_element(parser, child)
	
	@classmethod
	def parse_doc(cls, doc):
		parser = HtmlData(doc)
		HtmlData.parse_element(parser, parser.doc)
		return parser.parsed_html

def parse_html(html):
	doc = lhtml.fromstring(html)
	return HtmlData.parse_doc(doc)

# ---------------- comparison functions ---------------

def is_equal(value1, value2, is_para = False):
	base = value1.data
	test = value2.data
	if len(value1) == len(value2):
		values = []
		if isinstance(base, dict):
			for key in base:
				if base[key] == test[key]:
					values.append([key, 'equal', base[key], test[key]])
				else:
					values.append([key, 'different', base[key], test[key]])
			return values
		elif not is_para:
			i = 0
			while(i < len(value1)):
				if base[i] == test[i]:
					values.append(['', 'equal', base[i], test[i]])
				else:
					values.append(['', 'different', base[i], test[i]])
				i += 1
			return values
		else:
			i = 0
			while(i < len(value1)):
				if base[i] == test[i]:
					values.append(['', 'paragraph content equal', '', ''])
				else:
					values.append(['', 'paragraph content different', '', ''])
				i += 1
			return values
	else:
		return 'diff number of keys'

def compare_parsed_data(base_data, test_data):
	report_data = []
	if base_data.keys() == test_data.keys():
		for key in _html_data_keys:
			name = key + ':'
			report_data.append([name, is_equal(base_data[key], test_data[key])])
	return report_data

# ------------ file i/o --------------

def parse_html_file(html_file):
	html_file = os.path.expanduser(html_file)
	with open(html_file, "r") as f:
		return parse_html(f.read())

def write_file_items(report_data, txt_file):
	with open(txt_file, "w") as f:
		for tipe in report_data:
			f.write(tipe[0] + '\n')
			for line in tipe[1]:
				if isinstance(line, list):
					f.write(('  %10s%10s (base) %s  (test) %s\n' % (line[0], line[1], line[2], line[3])))
				else:
					f.write('\t' + tipe[1] + '\n')
					break
		
def main(args=None):
	if len(sys.argv) == 4:
		base_data = parse_html_file(sys.argv[1])
		test_data = parse_html_file(sys.argv[2])
		report_data = compare_parsed_data(base_data, test_data)
		write_file_items(report_data, sys.argv[3])
	else:
		print '3 arguments required'

if __name__ == '__main__':
	main()
