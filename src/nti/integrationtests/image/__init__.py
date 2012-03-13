import sys, os
import math, operator
from nti.integrationtests.image import Comparisons
from PIL import Image
import unittest

class Comparisons(unittest.TestCase):
    
    basePicDir = os.path.dirname(__file__) + "/basepics/"
    testPicDir = "/Volumes/WebServer/Documents/prealgebra/"
    
    @classmethod
    def setUpClass(cls):
    
        assert os.path.exists(cls.basePicDir), "cannot find base directory pictures"
        assert os.path.exists(cls.testPicDir), "cannot find test directory pictures"

    def compare(self, relPicPath):
        
        basePicPath = self.basePicDir + relPicPath
        testPicPath = self.testPicDir + relPicPath
        
        if not os.path.exists(basePicPath) and not os.path.exists(testPicPath):
            assert False, "could not find either picture"
        
        elif not os.path.exists(basePicPath):
            assert False, 'could not find the base picture'
        
        elif not os.path.exists(testPicPath):
            assert False, 'could not find the test picture'
        
        bh = Image.open(basePicPath).histogram()
        th = Image.open(testPicPath).histogram()
        
        rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, bh, th))/len(bh))
        
        assert rms == 0

    def test_icons_chapter_C1(self):
        relPicPath = "icons/chapters/C1.png"
        self.compare(relPicPath)
    
    def test_icons_up(self): 
        relPicPath = "icons/up.gif"
        self.compare(relPicPath)

    def test_thumbnails_sec_negation(self): 
        relPicPath = "thumbnails/sec-negation.png"
        self.compare(relPicPath)
    
if __name__ == '__main__':
    unittest.main()