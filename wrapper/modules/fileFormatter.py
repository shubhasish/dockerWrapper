import json
import pickledb
from config import WRAPPER_DB_PATH
class File:

    def __init__(self):
        pass

    def readFile(self,name):

        self.db = None
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH,False)
            self.SERVERS = self.db.get('servers')
        except Exception as e:
            pass
        return json.loads(contents)

    def writeFile(self,dict):
        try:
            file = open('shape.memory', 'w')
            file.writelines(json.dumps(dict))
            file.close()
        except Exception as e:
            print e