'''
Created on May 14, 2012

@author: ltesti
'''

import sys
import lxml.html as lhtml

from urlparse import urljoin

#from urlparse import urljoin

class ParseHtml(object):
    
    def __init__(self, doc, uri):
        self.base = uri
        self.doc = doc
        self.parsed_html = {'links':{}, 'span':{}, 'a':{}}
        
        self.url = urljoin
        self.text = lambda t: t
        self.datetime = lambda dt: dt
    
    def parse_ntiid(self, elem):
        tag = elem.tag
        if(tag == 'meta' and self.text(elem.get("name") == 'NTIID')):
            self.parsed_html['NTIID'] = [self.text(elem.get("content")), self.text(elem.get("name"))]
        for child in elem.getchildren():
            for _ in self.parse_ntiid(child):
                yield _
        return
    
    def parse_links(self, elem):
        tag = elem.tag
        if(tag == 'link' and self.text(elem.get('title') == 'Subtraction')):
            self.parsed_html['links']['subtration'] = [self.text(elem.get("href")), self.text(elem.get("rel")), self.text(elem.get("title"))]
        if(tag == 'link' and self.text(elem.get('title') == 'Multiplication')):
            self.parsed_html['links']['multiplication'] = [self.text(elem.get("href")), self.text(elem.get("rel")), self.text(elem.get("title"))]
        if(tag == 'link' and self.text(elem.get('title') == 'Properties of Arithmetic')):
            self.parsed_html['links']['properties_of_aritmetic'] = [self.text(elem.get("href")), self.text(elem.get("rel")), self.text(elem.get("title"))]
        for child in elem.getchildren():
            for _ in self.parse_links(child):
                yield _
        return
    
    def parse_span(self, elem):
        tag = elem.tag
        if(tag == 'span' and self.text(elem.get("class")) == 'ref'):
            self.parsed_html['span']['ref'] = [self.text(elem.get("class")), self.text(self.to_text(elem))]
        if(tag == 'span' and self.text(elem.get("class")) == 'label'):
            self.parsed_html['span']['label'] = [self.text(elem.get("class")), self.text(self.to_text(elem))]
        for child in elem.getchildren():
            for _ in self.parse_span(child):
                yield _
        return
    
    def parse_anchor_elems(self, elem):
        tag = elem.tag
        if(tag == 'a' and self.text(elem.get("name")) == 'a0000000566'):
            self.parsed_html['a']['name'] = [self.text(elem.get("name")) == 'a0000000566']
        if(tag == 'a' and self.text(elem.get("id")) == 'a0000000567'):
            self.parsed_html['a']['id'] = [self.text(elem.get("id")) == 'a0000000567', self.text(elem.get("name")) == 'a0000000567']
        for child in elem.getchildren():
            for _ in self.parse_anchor_elems(child):
                yield _
        return
    
    def parse_iframe_src_att(self):
        pass
    
    def parse_paragraphs(self):
        pass
    
    def to_text(self, elem):
        ret = elem.text or ""
        for child in elem.getchildren():
            ret += self.to_text(child)
            ret += child.tail or ""
        return ret
    
    @classmethod
    def parse_doc(cls, doc, uri):
        parser = ParseHtml(doc, uri)
        for elem in parser.parse_ntiid(parser.doc): pass
        for elem in parser.parse_links(parser.doc): pass
        for elem in parser.parse_span(parser.doc):pass
        for elem in parser.parse_anchor_elems(parser.doc):pass
        return parser.parsed_html
    
def items(html, types=None, uri=""):
    """
    list microdata as standard data types
    returns [{"properties": {name: [val1, ...], ...}, "id": id, "type": type}, ...]
    """
    doc = lhtml.fromstring(html)
    return ParseHtml.parse_doc(doc, uri)

def get_file_items(html_file, types=None, uri=""):
    with open(html_file, "r") as f:
        html = f.read()
        f.close()
        return items(html, types, uri)
        
def main(args=None):
    args = args or sys.argv[1:]
    return get_file_items(sys.argv[1]) if args else None

if __name__ == '__main__':
    from pprint import pprint
    pprint(main())