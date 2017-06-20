import json

class File:

    def __init__(self):
        pass

    def readFile(self,name):
        file = open(name,'r+')
        contents = file.read()
        file.close()
        return json.loads(contents)

    def writeFile(self,dict):
        try:
            file = open('shape.memory', 'w')
            file.writelines(json.dumps(dict))
            file.close()
        except Exception as e:
            print e