import json


class Parser(object):
    def __init__(self):
        self.jsonFile = open("config.json",'r+').read()
        self.jsonObject = json.loads(self.jsonFile)

    def getNode(self):
        return self.jsonObject['nodes']