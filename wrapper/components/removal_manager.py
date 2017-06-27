import os
from wrapper.modules.fileFormatter import File

class RemovalManager:
    def __init__(self):
        self.MASTER = dict()
        self.file = File()
        try:
            print "Reading Configuration File"
            self.config_file = self.file.readFile('config.json')
        except Exception as e:
            print e
            print "Exiting Node removal Process"
            os._exit(1)
        try:
            self.MASTER = self.file.readFile('shape.memory')
        except Exception as e:
            pass