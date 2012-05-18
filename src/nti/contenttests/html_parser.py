import os
import sys
import pprint
import lxml.html as lhtml
from collections import OrderedDict

from nltk import clean_html

# ----------- object classes ------------

class Element(object):
	def __repr__(self):
		return '%r%s' % (self.__class__.__name__, self)
	
class Meta(Element):
	
	def __init__(self, name, content):
		self.name = name
		self.content = content
	
	def __eq__(self, other):
		return self.name == other.name and self.content == other.content
	
	def __str__(self):
		return '(%s, %r)' % (self.name, self.content)
	
class Link(Element):
	
	def __init__(self, title, href, rel):
		self.rel = rel
		self.href = href
		self.title = title
	
	def __eq__(self, other):
		return  self.href == other.href and \
				self.rel == other.rel and \
				self.title == other.title

	def __str__(self):
		return '(%r, %r, %r)' % (self.title, self.rel, self.href)
	
class Span(Element):
	
	def __init__(self, clazz, text):
		self.text = text
		self.clazz = clazz
	
	def __eq__(self, other):
		return self.text == other.text and self.clazz == other.clazz
	
	def __str__(self):
		return '(%r,%r)' % (self.clazz, self.text)
	
class Anchor(Element):
	
	def __init__(self, _id, name):
		self.id = _id
		self.name = name
	
	def __eq__(self, other):
		return self.name == other.name and self.id == other.id
	
	def __str__(self):
		return '(%r, %r)' % (self.id, self.name)
	
class Image(Element):
	
	def __init__(self, style):
		self.style = style
	
	def __eq__(self, other):
		return self.style == other.style

	def __str__(self):
		return '(%r)' % self.style
	
class IFrame(Element):
	
	def __init__(self, src):
		self.src = src
	
	def __eq__(self, other):
		return self.src == other.src
	
	def __str__(self):
		return '(%r)' % self.src
	
class Paragraph(Element):
	
	def __init__(self, _id, text):
		self.id = _id
		self.text = clean_html(text)
	
	def __eq__(self, other):
		return self.id == other.id and self.text == other.text
	
	def __str__(self):
		return '(%r)' % self.id
	
	def __repr__(self):
		return '%r(%r, %r)' % (self.__class__.__name__, self.id, self.text)

# ------------ object collections ----------

_equal = 'equal'
_different = 'different'

class _ElementCollection(object):
	
	def idr(self, other):
		"""
		return a information difference report
		"""
		return ''
	
	def __len__(self):
		return len(self.data)
	
	def __str__(self):
		return str(self.data)
	
	def __repr__(self):
		return repr(self.data)

class _ArrayCollection(_ElementCollection):
	
	def __init__(self):
		self.data = []

	def add_element(self, info):
		self.data.append(info)
		
	def items(self):
		return self.data
	
	def idr(self, other):
		if len(other) != len(self):
			result = 'Different data size. %s vs %s' % (len(self), len(other))
		else:
			result = []
			for i in range(len(self) + 1):
				mo = self.data[i]
				to = other.data[i]
				if mo == to:
					result.append(('', _equal, mo, to))
				else:
					result.append(('', _different, mo, to))
		return result
		
	def __eq__(self, other):
		return self.data == other.data
	
class _MapCollection(_ElementCollection):

	def __init__(self):
		self.data = {}
		
	def add_value(self, key, value):
		self.data[key] = value
		
	def items(self):
		return self.data.items()
	
	def idr(self, other):
		result = []
		in_master = []
		
		for _id, mp in self.data.items():
			tp = other.data.get(_id, None)
			if not tp:
				in_master.append(_id,)
			elif mp == tp:
				result.append((_id, _equal, mp, tp))
			else:
				result.append((_id, _different, mp, tp))
				
		for _id in in_master:
			result.append((_id, 'missing in target', _id,''))
		
		for _id in other.data.keys():
			if _id not in self.data:
				result.append((_id, 'missing in master', _id,''))
				
		return result
	
	def keys(self):
		return self.data.keys()
	
	def has_key(self, key):
		return self.data.has_key(key)
	
	def __getitem__(self, key):
		return self.data[key]
	
	def __setitem__(self, key, value):
		self.data[key] = value
	
	def __eq__(self, other):
		result = len(self) == len(other)
		if result:
			for _id, mp in self.data.items():
				tp = other.data.get(_id, None)
				result = mp == tp
				if not result:
					break
		return result
	
class MetaCollection(_MapCollection):
	pass

class LinksCollection(_MapCollection):
	pass
		
class SpanCollection(_MapCollection):
	pass

class ParagraphCollection(_MapCollection):
	def __init__(self):
		self.data = OrderedDict()
		
class AnchorCollection(_ArrayCollection):
	pass
		
class ImageCollection(_ArrayCollection):
	pass
	
class IFrameCollection(_ArrayCollection):
	pass
IframeCollection = IFrameCollection

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
	
	def pprint(self, stream=None, indent=1):
		pprint.pprint(self.parsed_html, stream=stream, indent=indent)
		
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
			self.span.add_value(clazz, Span(clazz, self.to_text(elem)))

	def parse_anchor(self, elem):
		name, _id = elem.get("name"), elem.get("id")
		if name or _id:
			self.parsed_html['anchor'].add_element(Anchor(_id, name))

	def parse_image(self, elem):
		self.parsed_html['image'].add_element(Image(elem.get("style")))
	
	def parse_iframe(self, elem):
		self.parsed_html['iframe'].add_element(IFrame(elem.get("src")))
	
	def parse_paragraph(self, elem):
		_id, text = elem.get("id"), self.to_text(elem)
		self.parsed_html['paragraph'].add_value(_id, text)
	
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

def compare_parsed_data(base_data, test_data):
	report_data = []
	for key in _html_data_keys:
		name = key + ':'
		master = base_data.get(key, None)
		target = test_data.get(key, None)
		if master and target:
			report_data.append((name, master.idr(target)))
	return report_data

# ------------ file i/o --------------

def parse_html_file(html_file):
	html_file = os.path.expanduser(html_file)
	with open(html_file, "r") as f:
		return parse_html(f.read())

def write_file_items(report_data, txt_file):
	with open(txt_file, "w") as f:
		for key, info in report_data:
			f.write(key + '\n')
			if isinstance(info, (tuple,list)):
				for line in info:
					f.write(('  %10s%10s (base) %s  (test) %s\n' % (line[0], line[1], line[2], line[3])))
			else:
				f.write('\t%s\n' % info)
		
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
