import sys
import os
import lxml.html as lhtml
from nltk import clean_html

class Elements(object):
    
    def add_element(self, info, key=None):
        if key:
            self.data[key] = info
        else:
            self.data.append(info)
    
    @property
    def leng(self):
        return len(self.data)

class NTIID(Elements):
    
    def __init__(self):
        self.data = {}
        self.data['content'] = None
        

class Links(Elements):
    
    def __init__(self):
        self.data = {}
        self.data['next'] = None
        self.data['prev'] = None
        self.data['up'] = None
        
class Span(Elements):
    
    def __init__(self):
        self.data = {}
        self.data['ref'] = None
        self.data['label'] = None

class Anchor(Elements):
    
    def __init__(self):
        self.data = []
        
class Image(Elements):
    
    def __init__(self):
        self.data = []
        
class IFrame(Elements):
    
    def __init__(self):
        self.data = []
        
class Paragraph(Elements):
    
    def __init__(self):
        self.data = []

class HtmlData(object):
    
    def __init__(self, doc):
        self.doc = doc
        self.parsed_html = {
                            'ntiid'     : NTIID(),
                            'links'     : Links(),
                            'span'      : Span(),
                            'anchor'    : Anchor(),
                            'image'     : Image(),
                            'iframe'    : IFrame(),
                            'paragraph' : Paragraph()
                            }
    
    def parse_ntiid(self, elem):
        if elem.get("name") == 'NTIID':
            self.parsed_html['ntiid'].add_element(elem.get('content'), 'content')
    
    def parse_links(self, elem):
        rel = elem.get('rel')
        if rel == 'next':
            self.parsed_html['links'].add_element(elem.get("href"), 'next')
        elif rel == 'prev':
            self.parsed_html['links'].add_element(elem.get("href"), 'prev')
        elif rel == 'up':
            self.parsed_html['links'].add_element(elem.get("href"), 'up')
    
    def parse_span(self, elem):
        clazz = elem.get('class')
        if clazz == 'ref':
            self.parsed_html['span'].add_element(self.to_text(elem), 'ref')
        if clazz == 'label':
            self.parsed_html['span'].add_element(self.to_text(elem), 'label')
    
    def parse_anchor_elems(self, elem):
        self.parsed_html['anchor'].add_element([elem.get("name"), elem.get("id")])
    
    def parse_images(self, elem):
        self.parsed_html['image'].add_element(elem.get("style"))
    
    def parse_iframe_src_att(self, elem):
        self.parsed_html['iframe'].add_element(elem.get("src"))
    
    def parse_paragraphs(self, elem):
        self.parsed_html['paragraph'].add_element(self.to_text(elem))
    
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
            parser.parse_paragraphs(elem)
            
        for child in elem.getchildren():
            HtmlData.parse_element(parser, child)
    
    @classmethod
    def parse_doc(cls, doc):
        parser = HtmlData(doc)
        HtmlData.parse_element(parser, parser.doc)
        return parser.parsed_html

def is_equal(value1, value2, is_para = False):
    base = value1.data
    test = value2.data
    if value1.leng == value2.leng:
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
            while(i < value1.leng):
                if base[i] == test[i]:
                    values.append(['', 'equal', base[i], test[i]])
                else:
                    values.append(['', 'different', base[i], test[i]])
                i += 1
            return values
        else:
            i = 0
            while(i < value1.leng):
                if base[i] == test[i]:
                    values.append(['', 'paragraph content equal', '', ''])
                else:
                    values.append(['', 'paragraph content different', '', ''])
                i += 1
            return values
    else:
        return 'dif numb of keys'

def compare_parsed_data(base_data, test_data):
    report_data = []
    if(base_data.keys() == test_data.keys()):
        report_data.append(['ntiid:', is_equal(base_data['ntiid'], test_data['ntiid'])])
        report_data.append(['links:', is_equal(base_data['links'], test_data['links'])])
        report_data.append(['span:', is_equal(base_data['span'], test_data['span'])])
        report_data.append(['anchor:', is_equal(base_data['anchor'], test_data['anchor'])])
        report_data.append(['image:', is_equal(base_data['image'], test_data['image'])])
        report_data.append(['iframe:', is_equal(base_data['iframe'], test_data['iframe'])])
        report_data.append(['paragraph:', is_equal(base_data['paragraph'], test_data['paragraph'], True)])
        return report_data
    else:
        pass

def items(html):
    doc = lhtml.fromstring(html)
    return HtmlData.parse_doc(doc)

def get_file_items(html_file):
    with open(html_file, "r") as f:
        html = f.read()
        f.close()
        return items(html)

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