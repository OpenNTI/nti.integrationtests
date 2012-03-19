import sys, os
import math, operator
from PIL import Image

# stores image info
class FileStatis(object):
    
    file_name = None
    
    base_pic_path = None
    test_pic_path = None
    rel_path = None
    
    file_in_base = False
    file_in_test = False
    file_statis = None
    
    file_size = 0
    
    def __init__(self, file_name, file_rel_path, file_size, base_dir_path=None, test_dir_path=None, file_in_base=False, file_in_test=False):
        self.file_name = file_name
        self.rel_path = file_rel_path
        self.file_size = file_size
        if base_dir_path: self.base_pic_path = base_dir_path + file_rel_path + file_name
        if test_dir_path: self.test_pic_path = test_dir_path + file_rel_path + file_name
        if file_in_base: self.file_in_base = True 
        if file_in_test: self.file_in_test = True

    def found_base_file(self, path):
        self.base_pic_path = path + self.file_name
        self.file_in_base = True
    
    def found_test_file(self, path):
        self.test_pic_path = path + self.file_name
        self.file_in_test = True
    
    def check_statis(self):
        if not self.file_in_base: self.file_statis = 'pic not in base pics'
        elif not self.file_in_test: self.file_statis = 'pic not in test pics'
        else:
            bh = Image.open(self.base_pic_path).histogram()
            th = Image.open(self.test_pic_path).histogram()
            rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, bh, th))/len(bh))
            if rms == float(0.0): self.file_statis = 'images are equal'
            else: self.file_statis = 'images are not equal'

extentions = ['jpg', 'png', 'bmp', 'gif']

def check_paths(basePicDir, testPicDir):
    assert os.path.exists(basePicDir), "cannot find base directory pictures"
    assert os.path.exists(testPicDir), "cannot find test directory pictures"
                
def store_pics(pic_data, abs_path, rel_path="/", is_base_pic=True):
    path = abs_path + rel_path
    pic_data['Items'] = pic_data.get('Items', [])
    items = os.listdir(path)
    for item in items:
        if os.path.isdir(path + '/' + item): 
            pic_data[item] = pic_data.get(item, {})
            store_pics(pic_data[item], abs_path, rel_path + '/' + item, is_base_pic)
        else:
            not_found = True
            for pic in pic_data['Items']:
                if item == pic.file_name and is_base_pic:
                    pic.found_base_file(path)
                    not_found = False
                elif item == pic.file_name:
                    pic.found_test_file(path)
                    not_found = False
            if not_found and len(item.split(".")) is 2 and item.split(".")[1] in extentions and is_base_pic:
                newPic = FileStatis(item, rel_path, os.path.getsize(path+item), base_dir_path=abs_path, file_in_base=True)
                pic_data['Items'].append(newPic)
            elif not_found and len(item.split(".")) is 2 and item.split(".")[1] in extentions:
                newPic = FileStatis(item, rel_path, os.path.getsize(path+item), base_dir_path=abs_path, file_in_test=True)
                pic_data['Items'].append(newPic)
        
def write_pic_to_file(pic_data, txt_file_path):
    for key in pic_data.keys():
        if isinstance(pic_data[key], dict):
            write_pic_to_file(pic_data[key], txt_file_path)
        elif isinstance(pic_data[key], list):
            for pic in pic_data[key]:
                pic.check_statis()
#                f = open(txt_file_path, 'w')
#                f.write('name:' + pic.file_name + ', path: ' + pic.rel_path + ', file size: ' + str(pic.file_size) + ', result: ' + pic.file_statis)
                print 'name:' + pic.file_name + ', path: ' + pic.rel_path + ', file size: ' + str(pic.file_size) + ', result: ' + pic.file_statis
    
        
def run_tests():
    base_pic_dir = sys.argv[1]
    test_pic_dir = sys.argv[2]
    txt_file     = sys.argv[3]
    check_paths(base_pic_dir, test_pic_dir)
    pic_data = {}
    store_pics(pic_data, base_pic_dir)
    store_pics(pic_data, test_pic_dir, is_base_pic=False)
    write_pic_to_file(pic_data, txt_file)

if __name__ == '__main__':
    run_tests()