import json
import pickledb
from config import WRAPPER_DB_PATH
class File:

    def __init__(self):
        pass

    def readFile(self,name):

        self.file = None
        try:
            self.file = open(name,'r+')
            self.contents = self.file.read()
            print "===================================Configurations======================================="
            print self.contents
            print "========================================================================================\n"
        except Exception as e:
            pass
        return json.loads(self.contents)

    def writeFile(self,dict):
        try:
            file = open('shape.memory', 'w')
            file.writelines(json.dumps(dict))
            file.close()
        except Exception as e:
            print e