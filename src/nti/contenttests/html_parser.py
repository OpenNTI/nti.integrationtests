'''
Created on May 14, 2012

@author: ltesti
'''

import sys
import lxml.html as lhtml

#from urlparse import urljoin

class HtmlData(object):
    
    def __init__(self, doc):
        self.doc = doc
        self.parsed_html = {'links':{}, 'span':{}, 'attributes':[], 'img':[], 'iframe':[], 'paragraph':[]}
        self.text = lambda t: t
    
    def parse_ntiid(self, elem):
        if(self.text(elem.get("name") == 'NTIID')):
            self.parsed_html['NTIID'] = [self.text(elem.get("content")), self.text(elem.get("name"))]
    
    def parse_links(self, elem):
        if(self.text(elem.get('rel') == 'next')):
            self.parsed_html['links']['next'] = [self.text(elem.get("href"))]
        if(self.text(elem.get('rel') == 'prev')):
            self.parsed_html['links']['prev'] = [self.text(elem.get("href"))]
        if(self.text(elem.get('rel') == 'up')):
            self.parsed_html['links']['up'] = [self.text(elem.get("href"))]
    
    def parse_span(self, elem):
        if(self.text(elem.get("class")) == 'ref'):
            self.parsed_html['span']['ref'] = [self.text(self.to_text(elem))]
        if(self.text(elem.get("class")) == 'label'):
            self.parsed_html['span']['label'] = [self.text(self.to_text(elem))]
    
    def parse_anchor_elems(self, elem):
        self.parsed_html['attributes'].append([self.text(elem.get("name")), self.text(elem.get("id"))])
    
    def parse_images(self, elem):
        self.parsed_html['img'].append(self.text(elem.get("style")))
    
    def parse_iframe_src_att(self, elem):
        self.parsed_html['iframe'].append(self.text(elem.get("src")))
    
    def parse_paragraphs(self, elem):
        paragraph = []
        for child in elem.getchildren():
            tag = child.tag
            if(tag == 'a'):
                paragraph.append([self.text(child.get('name')), self.text(child.get('id'))])
            if(tag == 'span'):
                paragraph.append(self.text(self.to_text(elem)))
        return paragraph
    
    def to_text(self, elem):
        ret = elem.text or ""
        for child in elem.getchildren():
            ret += self.to_text(child)
            ret += child.tail or ""
        return ret
    
    @classmethod
    def parse_element(cls, parser, elem):
        tag = elem.tag
        if(tag == 'meta'):parser.parse_ntiid(elem)
        if(tag == 'link'):parser.parse_links(elem)
        if(tag == 'span'):parser.parse_span(elem)
        if(tag == 'a'):parser.parse_anchor_elems(elem)
        if(tag == 'img'):parser.parse_images(elem)
        if(tag == 'iframe'): parser.parse_iframe_src_att(elem)
        if(tag == 'p'):
            paragraph = parser.parse_paragraphs(elem)
            parser.parsed_html['paragraph'].append(paragraph)
        for child in elem.getchildren():
            for _ in HtmlData.parse_element(parser, child):
                yield _
        return
    
    @classmethod
    def parse_doc(cls, doc):
        parser = HtmlData(doc)
        for elem in parser.parse_element(parser, parser.doc): pass
        return parser.parsed_html
    
def items(html, types=None):
    doc = lhtml.fromstring(html)
    return HtmlData.parse_doc(doc)

def get_file_items(html_file, types=None):
    with open(html_file, "r") as f:
        html = f.read()
        f.close()
        return items(html, types)
        
def main(args=None):
    args = args or sys.argv[1:]
    return get_file_items(sys.argv[1]) if args else None

if __name__ == '__main__':
    from pprint import pprint
    pprint(main())