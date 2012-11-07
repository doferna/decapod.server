import cherrypy
from cherrypy.test import helper
import os
import sys
import re
import shutil
import simplejson as json

sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('..', '..', 'utils')))
import calibrator
import calibrateServer
from utils import io, image
from serverTestCase import ServerTestCase

DATA_DIR = os.path.abspath("data")
MOCK_DATA_DIR = os.path.abspath("mockData")

CONFIG = {
    "/": {
        "tools.staticdir.root": os.getcwd(),
        "request.dispatch": cherrypy.dispatch.MethodDispatcher()
    },
    "/lib": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": "../../../decapod-ui/lib"
    },
    "/calibrate": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": "../../../decapod-ui/calibrate"
    },
    "/core": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": "../../../decapod-ui/core"
    },
    "/data": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": "data"
    }
}

def setup_server(config=CONFIG):
    calibrateServer.mountApp(config)
    
def teardown_server(dir=DATA_DIR):
    io.rmTree(dir)
    sys.exit()
            
class TestConfig(helper.CPWebCase):
    # hardcoding due to the fact that setup_server can't take any arguments, not even "self"
    def customServerSetup():
        setup_server({
            "global": {
                "server.socket_host": "0.0.0.0"
            }
        })
    
    setup_server = staticmethod(customServerSetup)
    teardown_server = staticmethod(teardown_server)
    
    def test_01_socket_host(self):
        self.assertEquals("0.0.0.0", cherrypy.config["server.socket_host"])

class TestRoot(ServerTestCase):
    rootURL = "/"
    expectedRedirectURL = "/calibrate/html/calibrator.html"
    
    setup_server = staticmethod(setup_server)
    teardown_server = staticmethod(teardown_server)
    
    def test_01_get(self):
        self.getPage(self.rootURL)
        self.assertStatus(301)
        self.assertHeader("Location", cherrypy.url(self.expectedRedirectURL), "Assert that the Location is set to the redirect URL")
        
        
    def test_02_unsupportedMethods(self):
        self.assertUnsupportedHTTPMethods(self.rootURL, ["PUT", "POST", "DELETE"])
        
    def test_03_redirectURL(self):
        self.getPage(self.expectedRedirectURL)
        self.assertStatus(200)

class TestCalibrate(ServerTestCase):
    url = "/calibrate/"
    
    setup_server = staticmethod(setup_server)
    teardown_server = staticmethod(teardown_server)
    
    def setUp(self):
        io.makeDirs(DATA_DIR)
    
    def tearDown(self):
        io.rmTree(DATA_DIR)
    
    def test_01_unsupportedMethods(self):
        self.assertUnsupportedHTTPMethods(self.url, ["POST"])
        
    def test_02_get(self):
        self.getPage(self.url)
        self.assertStatus(200)
        self.assertDictEqual({"status": calibrator.CALIBRATE_READY}, json.loads(self.body))
        
    def test_03_get_complete(self):
        expected = {"status": calibrator.CALIBRATE_COMPLETE}
        io.writeToJSONFile(expected, os.path.join(DATA_DIR, "status.json"));
        self.getPage(self.url)
        self.assertStatus(200)
        body = json.loads(self.body)
        self.assertEquals(calibrator.CALIBRATE_COMPLETE, body["status"])
        
        regexPattern = "http://127.0.0.1:\d*/data/calibration.zip"
        regex = re.compile(regexPattern)
        self.assertTrue(regex.findall(body["url"]))
        
    def test_04_delete(self):
        self.getPage(self.url, method="DELETE")
        self.assertStatus(204)

    def test_05_delete_error(self):
        io.writeToJSONFile({"status": calibrator.CALIBRATE_IN_PROGRESS}, os.path.join(DATA_DIR, "status.json"));
        self.getPage(self.url, method="DELETE")
        self.assertStatus(409)

class TestImages(ServerTestCase):
    url = "/images/"
    
    setup_server = staticmethod(setup_server)
    teardown_server = staticmethod(teardown_server)
    
    def setUp(self):
        io.makeDirs(DATA_DIR)
    
    def tearDown(self):
        io.rmTree(DATA_DIR)
        
    def tests_02_get_none(self):
        self.getPage(self.url)
        self.assertStatus(404)
        
    def tests_03_get_error_code(self):
        unpackedDir = os.path.join(DATA_DIR, "unpacked")
        io.makeDirs(unpackedDir)
        
        self.getPage(self.url)
        self.assertStatus(500)
        self.assertDictEqual({'msg': 'Selected archive does not appear to have stereo images.', 'ERROR_CODE': 'NO_STEREO_IMAGES'}, json.loads(self.body))
        
    def tests_04_get(self):
        unpackedDir = os.path.join(DATA_DIR, "unpacked")
        io.makeDirs(unpackedDir)
        for i in range(0, calibrator.REQUIRED_STEREO_IMAGES):
            shutil.copyfile(os.path.join(MOCK_DATA_DIR, "capture-0_1.jpg"), os.path.join(unpackedDir, "capture-{0}_1.jpg".format(i)))
            shutil.copyfile(os.path.join(MOCK_DATA_DIR, "capture-0_2.jpg"), os.path.join(unpackedDir, "capture-{0}_2.jpg".format(i)))

        self.getPage(self.url)
        self.assertStatus(200)
        self.assertDictEqual({"numOfStereoImages": calibrator.REQUIRED_STEREO_IMAGES}, json.loads(self.body))
        
    def tests_05_delete(self):
        unpackedDir = os.path.join(DATA_DIR, "unpacked")
        self.getPage(self.url, method="DELETE")
        self.assertStatus(204)
        self.assertFalse(os.path.exists(unpackedDir))
        
    def tests_06_delete_inProgress(self):
        unpackedDir = os.path.join(DATA_DIR, "unpacked")
        io.makeDirs(unpackedDir)
        io.writeToJSONFile({"status": calibrator.CALIBRATE_IN_PROGRESS}, os.path.join(DATA_DIR, "status.json"));
        self.getPage(self.url, method="DELETE")
        self.assertStatus(409)
        self.assertInBody("Calibration in progress, cannot delete until this process has finished")
        self.assertTrue(os.path.exists(unpackedDir))
        
    def tests_07_put(self):
        self.uploadFile(self.url, os.path.join(MOCK_DATA_DIR, "empty_captures.zip"), method="PUT")
        self.assertStatus(500)
        self.assertDictEqual({'msg': 'Selected archive does not appear to have stereo images.', 'ERROR_CODE': 'NO_STEREO_IMAGES'}, json.loads(self.body))
        
    def tests_08_put_inProgress(self):
        io.writeToJSONFile({"status": calibrator.CALIBRATE_IN_PROGRESS}, os.path.join(DATA_DIR, "status.json"));
        self.uploadFile(self.url, os.path.join(MOCK_DATA_DIR, "empty_captures.zip"), method="PUT")
        self.assertStatus(409)
        self.assertInBody("Calibration currently in progress, cannot accept another zip until this process has finished")
        
    def tests_09_put_badZip(self):
        self.uploadFile(self.url, os.path.join(MOCK_DATA_DIR, "capture-0_1.jpg"), method="PUT")
        self.assertStatus(500)

if __name__ == '__main__':
    import nose
    nose.runmodule()