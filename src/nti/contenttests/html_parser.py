import sys
import lxml.html as lhtml
from nltk import clean_html

class HtmlData(object):
    
    def __init__(self, doc):
        self.doc = doc
        self.parsed_html = {'links':{}, 'span':{}, 'attributes':[], 'img':[], 'iframe':[], 'paragraph':[]}
    
    def parse_ntiid(self, elem):
        if elem.get("name") == 'NTIID':
            self.parsed_html['NTIID'] = (elem.get("content"), elem.get("name"))
    
    def parse_links(self, elem):
        if elem.get('rel') == 'next':
            self.parsed_html['links']['next'] = elem.get("href")
        elif elem.get('rel') == 'prev':
            self.parsed_html['links']['prev'] = elem.get("href")
        elif elem.get('rel') == 'up':
            self.parsed_html['links']['up'] = elem.get("href")
    
    def parse_span(self, elem):
        if elem.get("class") == 'ref':
            self.parsed_html['span']['ref'] = self.to_text(elem)
        if elem.get("class") == 'label':
            self.parsed_html['span']['label'] = self.to_text(elem)
    
    def parse_anchor_elems(self, elem):
        self.parsed_html['attributes'].append((elem.get("name"), elem.get("id")))
    
    def parse_images(self, elem):
        self.parsed_html['img'].append(elem.get("style"))
    
    def parse_iframe_src_att(self, elem):
        self.parsed_html['iframe'].append(elem.get("src"))
    
    def parse_paragraphs(self, elem):
        text = self.to_text(elem)
        text = clean_html(text)
        return text
    
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
        if tag == 'meta': 
            parser.parse_ntiid(elem)
        elif tag == 'link':
            parser.parse_links(elem)
        elif tag == 'span':
            parser.parse_span(elem)
        elif tag == 'a':
            parser.parse_anchor_elems(elem)
        elif tag == 'img':
            parser.parse_images(elem)
        elif tag == 'iframe':
            parser.parse_iframe_src_att(elem)
        elif tag == 'p':
            paragraph = parser.parse_paragraphs(elem)
            parser.parsed_html['paragraph'].append(paragraph)
            
        for child in elem.getchildren():
            HtmlData.parse_element(parser, child)
    
    @classmethod
    def parse_doc(cls, doc):
        parser = HtmlData(doc)
        parser.parse_element(parser, parser.doc)
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