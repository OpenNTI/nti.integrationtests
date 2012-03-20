import sys, os
import math, operator
from PIL import Image

extentions = ['jpg', 'png', 'bmp', 'gif']

def check_paths(basePicDir, testPicDir, txt_file):
    assert os.path.exists(basePicDir), "cannot find base directory pictures"
    assert os.path.exists(testPicDir), "cannot find test directory pictures"
    assert os.path.exists(txt_file), "cannot find target txt_file"
                
def store_pics(abs_path, rel_path="/"):
    path = abs_path + rel_path
    pic_data = {}
    items = os.listdir(path)
    for item in items:
        if os.path.isdir(path + '/' + item): 
            pic_data[item] = store_pics(abs_path, rel_path + item + '/')
        else:
            if len(item.split(".")) is 2 and item.split(".")[1] in extentions:
                pic_data[item] = rel_path + item
    return pic_data
#                newPic = FileStatis(item, rel_path, os.path.getsize(path+item), base_dir_path=abs_path, file_in_base=True)
        
def compare_pics(base_pic_data, test_pic_data, f, files):
    base_keys = base_pic_data.keys()
    test_keys = test_pic_data.keys()
    for key in base_keys:
        if key in test_keys:
            base_key = base_pic_data[key]
            test_key = test_pic_data[key]
            del(base_pic_data[key])
            del(test_pic_data[key])
            if isinstance(base_key, dict) and isinstance(test_key, dict):
                compare_pics(base_key, test_key, f, files)
            elif isinstance(base_key, dict): pass #deal with later
            elif isinstance(test_key, dict): pass #deal with later
            else:
                bh = Image.open(files['base_pic_dir'] + base_key).histogram()
                th = Image.open(files['test_pic_dir'] + test_key).histogram()
                rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, bh, th))/len(bh))
                if rms == 0.0:
                    f.write('name: ' + key + ', file path: ' + base_key + ', file size: ' + str(os.path.getsize(files['base_pic_dir'] + base_key))  + ', assessment: pictures are equivalent' + '\n')
                else:
                    f.write('name: ' + key + ', file path: ' + base_key + ', file size of base: ' + str(os.path.getsize(files['base_pic_dir'] + base_key))  + ', file size of test: ' + str(os.path.getsize(files['test_pic_dir'] + test_key))  + ', assessment: pictures are not equivalent' + '\n')
    for key in base_pic_data.keys():
        f.write('name: ' + key + ', file path: ' + base_pic_data[key] + ', file size: ' + str(os.path.getsize(files['base_pic_dir'] + base_pic_data[key]))  + ', assessment: picture only found in base pics' + '\n')
    for key in test_pic_data.keys():
        f.write('name: ' + key + ', file path: ' + test_pic_data[key] + ', file size: ' + str(os.path.getsize(files['test_pic_dir'] + test_pic_data[key]))  + ', assessment: picture only found in test pics' + '\n')
                
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