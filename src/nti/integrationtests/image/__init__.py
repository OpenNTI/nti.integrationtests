import sys, os, re
import math, operator
from PIL import Image

extentions = '.+(jpeg|png|gif|bmp)'
noextention = '\w*\.'
toManyExtentions = '(\w*\.\w*\.)'

def check_paths(basePicDir, testPicDir, txt_file):
    assert os.path.exists(basePicDir), "cannot find base directory pictures"
    assert os.path.exists(testPicDir), "cannot find test directory pictures"
    assert os.path.exists(txt_file),   "cannot find target txt_file"
                
def store_pics(abs_path):
    abs_path = abs_path + '/' if abs_path[len(abs_path) -1] != '/' else abs_path
    pic_data = {}
    items = os.listdir(abs_path)
    for item in items:
        if os.path.isdir(abs_path + '/' + item): 
            pic_data[item] = store_pics(abs_path + item)
        else:
            if not (not re.match(noextention, item) or re.match(toManyExtentions, item)) and re.match(extentions, item):
                pic_data[item] = item
    return pic_data
        
def compare_pics(base_pic_data, test_pic_data, f, files, rel_path=''):
    files['base_pic_dir'] = files['base_pic_dir'] + '/' if files['base_pic_dir'][len(files['base_pic_dir']) -1] != '/' else files['base_pic_dir']
    files['test_pic_dir'] = files['test_pic_dir'] + '/' if files['test_pic_dir'][len(files['test_pic_dir']) -1] != '/' else files['test_pic_dir']
    base_keys = base_pic_data.keys()
    test_keys = test_pic_data.keys()
    for key in base_keys:
        if key in test_keys:
            base_key = base_pic_data[key]
            test_key = test_pic_data[key]
            del(base_pic_data[key])
            del(test_pic_data[key])
            if isinstance(base_key, dict) and isinstance(test_key, dict):
                local_path = rel_path + key + '/'
                compare_pics(base_key, test_key, f, files, local_path)
            elif isinstance(base_key, dict): 
                f.write(('name: %s, file path: %s, assessment: %s') % (key, local_path+key, ('%s is a dir in the base set of pictures and a picture in the rendered content' % key)))
            elif isinstance(test_key, dict):
                f.write(('name: %s, file path: %s, assessment: %s') % (key, local_path+key, ('%s is a dir in the rendered set of pictures and a picture in the base content' % key)))
            else:
                bh = Image.open(files['base_pic_dir'] + rel_path + base_key).histogram()
                th = Image.open(files['test_pic_dir'] + rel_path + test_key).histogram()
                rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, bh, th))/len(bh))
                print_path = '~/' + rel_path + base_key
                base_file_size = os.path.getsize(files['base_pic_dir'] + base_key)
                test_file_size = os.path.getsize(files['test_pic_dir'] + test_key)
                if rms == 0.0:
                    f.write(('name: %s, file path: %s, file size: %d, assessment: %s\n') % (key, print_path, base_file_size, 'pictures are equivalent'))
                else:
                    f.write(('name: %s, file path: %s, file size(base): %d, file size(rendered): %d, assessment: %s\n') % 
                            (key, print_path, base_file_size, test_file_size, 'pictures are not equivalent'))
    for key in base_pic_data.keys():
        print_path = '~/' + rel_path + key
        file_size = os.path.getsize(files['base_pic_dir'] + key)
        f.write(('name: %s, file path: %s, file size: %d, assessment: %s\n') % (key, print_path, file_size, 'picture only found in base pics'))
    for key in test_pic_data.keys():
        print_path = '~/' + rel_path + key
        file_size = os.path.getsize(files['test_pic_dir'] + key)
        f.write(('name: %s, file path: %s, file size: %d, assessment: %s\n') % (key, print_path, file_size, 'picture only found in rendered pics'))
                
def write_pic_to_file(base_pic_data, test_pic_data, files):
    f = open(files['txt_file'], 'w')
    compare_pics(base_pic_data, test_pic_data, f, files)
    f.close()
    
        
def run_tests():
    base_pic_dir = sys.argv[1]
    test_pic_dir = sys.argv[2]
    txt_file     = sys.argv[3]
    check_paths(base_pic_dir, test_pic_dir, txt_file)
    base_pic_data = store_pics(base_pic_dir)
    test_pic_data = store_pics(test_pic_dir)
    files = {'base_pic_dir':base_pic_dir, 'test_pic_dir':test_pic_dir, 'txt_file':txt_file}
    write_pic_to_file(base_pic_data, test_pic_data, files)

if __name__ == '__main__':
    run_tests()