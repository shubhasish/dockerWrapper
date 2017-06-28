import os
from modules.fileFormatter import File
from config import DM_URL
from config import dir_path
from modules.machine import Machine

class RemovalManager:
    def __init__(self):
        self.MASTER = dict()
        self.file = File()
        self.manager = Machine(path=DM_URL)
        try:
            self.MASTER = self.file.readFile('shape.memory')
        except Exception as e:
            print e
            #print "\n Check if you have already initialized cluster in this folder...."

    def removeNodes(self,name="all"):
        if name[0].lower() == "all":
            print "All nodes will  be deleted, and the workspace will be reseted."
            for nodes in self.MASTER.keys():
                print "Deleting ...\n%s\t%s"%(nodes,self.MASTER[nodes]['ip'])
                self.manager.rm(nodes)
            os.remove(dir_path+"/shape.memory")
        else:
            print "Following nodes will be deleted"
            for nodes in name:
                print "Deleting ...\n%s\t%s"%(nodes,self.MASTER[nodes]['ip'])
                self.manager.rm(nodes)
                del self.MASTER[nodes]
            self.file.writeFile('shape.memory')
