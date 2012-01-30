import os
import glob
import sys
import shutil
import mimetypes
sys.path.append(os.path.abspath('..'))
import resourcesource

IMAGES_TEST_DIR = "data/library/book/images/"

def cleanUpDir(dir):
    filePaths = glob.glob(dir + "/*")
    for filePath in filePaths:
        os.remove(filePath)  
        
def cleanUpImages():
    cleanUpDir(IMAGES_TEST_DIR)

def deleteTestImagesDir():
    shutil.rmtree(IMAGES_TEST_DIR)
    
class mockResourceSource(object):
    
    def __init__(self, mockResources):
        self.mockResources = mockResources

    def url(self, virtualPath, absolute=True):
        resource, path = resourcesource.parseVirtualPath(virtualPath)
        section = self.mockResources[resource]["url"]
        return os.path.join(section, path)

    def path(self, virtualPath, absolute=True, config=None):
        resource, path = resourcesource.parseVirtualPath(virtualPath)
        section = self.mockResources[resource]["path"]
        fspath = os.path.join(section, path)
        return os.path.join(os.getcwd(), fspath) if absolute else fspath

class mockFileStream(object):
    def __init__(self, filePath):
        name, extension = os.path.splitext(filePath)
        self.file = open(filePath, 'rb')
        self.content_type = mockMimeType(filePath)

class mockMimeType(object):
    def __init__(self, filePath):
        self.value = mimetypes.guess_type(filePath)[0]
