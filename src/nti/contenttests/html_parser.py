import sys
import os
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

def is_equal(value1, value2):
    if(value1 == value2):
        return 'equal'
    else:
        return 'different'

def compare_parsed_data(base_data, test_data):
    report_data = []
    if(base_data.keys() == test_data.keys()):
        report_data.append(['NTIID:', ''])
        report_data.append(['\tNTIID:', is_equal(base_data['NTIID'], test_data['NTIID'])])
        report_data.append(['links:', ''])
        report_data.append(['\tnext: ', is_equal(base_data['links']['next'], test_data['links']['next'])])
        report_data.append(['\tprev: ', is_equal(base_data['links']['prev'], test_data['links']['prev'])])
        report_data.append(['\tup:   ', is_equal(base_data['links']['up'], test_data['links']['up'])])
        report_data.append(['span', ''])
        report_data.append(['\tref:  ', is_equal(base_data['span']['ref'], test_data['span']['ref'])])
        report_data.append(['\tlabel:', is_equal(base_data['span']['ref'], test_data['span']['ref'])])
#        report_data.append(['img:', ''])
        return report_data
    else:
        pass

def items(html, types=None):
    doc = lhtml.fromstring(html)
    return HtmlData.parse_doc(doc)

def get_file_items(html_file, types=None):
    with open(html_file, "r") as f:
        html = f.read()
        f.close()
        return items(html, types)

def write_file_items(report_data, txt_file):
    with open(txt_file, "w") as f:
        for line in report_data:
            print line
            f.write(('%s %10s\n' % (line[0], line[1])))
  
def is_prop_path(path, extention): 
    return os.path.isfile(path) and (path.split(".")[1] == extention)
        
def send_error(error):
    print error
        
def main(args=None):
    if(len(sys.argv) == 4):
        if(is_prop_path(sys.argv[1], 'html') and is_prop_path(sys.argv[2], 'html') and is_prop_path(sys.argv[3], 'txt')):
            base_data = get_file_items(sys.argv[1])
            test_data = get_file_items(sys.argv[2])
            report_data = compare_parsed_data(base_data, test_data)
            write_file_items(report_data, sys.argv[3])
        else: send_error('improper file types')
    else:
        send_error('3 arguments required')

if __name__ == '__main__':
    main()