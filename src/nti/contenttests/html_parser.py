import sys
import os
import lxml.html as lhtml
from nltk import clean_html

# ----------- object classes ------------

class MetaData(object):
    
    def __init__(self, content):
        self.content = content
    
    @property
    def get_values(self):
        return self.content
    
class LinkData(object):
    
    def __init__(self, href):
        self.href = href
        
    @property
    def get_values(self):
        return self.href
    
class SpanData(object):
    
    def __init__(self, text):
        self.text = text
        
    @property
    def get_values(self):
        return self.text
    
class AnchorData(object):
    
    def __init__(self, name, Id):
        self.name = name
        self.Id = Id
       
    @property 
    def get_values(self):
        return self.name, self.Id
    
class ImageData(object):
    
    def __init__(self, style):
        self.style = style
        
    @property
    def get_values(self):
        return self.style
    
class IFrameData(object):
    
    def __init__(self, src):
        self.src = src
    
    @property
    def get_values(self):
        return self.src
    
class ParagraphData(object):
    
    def __init__(self, name, text):
        self.name = name
        text = clean_html(text)
        self.text = text
        
    @property
    def get_values(self):
        return self.name, self.text

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
        self.data['next'] = None
        self.data['prev'] = None
        self.data['up'] = None
        
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
        
class ParagraphCollection(ElementsCollection):
    
    def __init__(self):
        self.data = []

# ------------ add data to collections -------------

class HtmlData(object):
    
    def __init__(self, doc):
        self.doc = doc
        self.parsed_html = {
                            'ntiid'     : MetaCollection(),
                            'links'     : LinksCollection(),
                            'span'      : SpanCollection(),
                            'anchor'    : AnchorCollection(),
                            'image'     : ImageCollection(),
                            'iframe'    : IFrameCollection(),
                            'paragraph' : ParagraphCollection()
                            }
    
    def parse_meta(self, elem):
        if elem.get("name") == 'NTIID':
            self.parsed_html['ntiid'].add_value('content', MetaData(elem.get('content')))
    
    def parse_links(self, elem):
        rel = elem.get('rel')
        if rel == 'next':
            self.parsed_html['links'].add_value('next', LinkData(LinkData(elem.get("href"))))
        elif rel == 'prev':
            self.parsed_html['links'].add_value('prev', LinkData(elem.get("href")))
        elif rel == 'up':
            self.parsed_html['links'].add_value('up', LinkData(elem.get("href")))
    
    def parse_span(self, elem):
        clazz = elem.get('class')
        if clazz == 'ref':
            self.parsed_html['span'].add_value('ref', SpanData(self.to_text(elem)))
        if clazz == 'label':
            self.parsed_html['span'].add_value('label', SpanData(self.to_text(elem)))
    
    def parse_anchor_elems(self, elem):
        self.parsed_html['anchor'].add_element(AnchorData(elem.get("name"), elem.get("id")))
    
    def parse_images(self, elem):
        self.parsed_html['image'].add_element(ImageData(elem.get("style")))
    
    def parse_iframe_src_att(self, elem):
        self.parsed_html['iframe'].add_element(IFrameData(elem.get("src")))
    
    def parse_paragraphs(self, elem):
        self.parsed_html['paragraph'].add_element(ParagraphData(elem.get("name"), self.to_text(elem)))
    
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
            parser.parse_meta(elem)
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

def items(html):
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
                if base[key].get_values == test[key].get_values:
                    values.append([key, 'equal', base[key].get_values, test[key].get_values])
                else:
                    values.append([key, 'different', base[key].get_values, test[key].get_values])
            return values
        elif not is_para:
            i = 0
            while(i < len(value1)):
                if base[i].get_values == test[i].get_values:
                    values.append(['', 'equal', base[i].get_values, test[i].get_values])
                else:
                    values.append(['', 'different', base[i].get_values, test[i].get_values])
                i += 1
            return values
        else:
            i = 0
            while(i < len(value1)):
                if base[i].get_values == test[i].get_values:
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

# ------------ file i/o --------------

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