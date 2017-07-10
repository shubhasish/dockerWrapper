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

    def removeNodes(self,nodes="all"):
        for node in nodes:
            if "all" in nodes:
                print "All nodes will  be deleted, and the workspace will be reseted."
                for nodes in self.MASTER.keys():
                    print "Deleting ...\n%s\t%s"%(nodes,self.MASTER[nodes]['ip'])
                    self.manager.rm(nodes,force=True)
                os.remove(dir_path+"/shape.memory")
                os._exit(0)
            else:
                print "%s will be deleted"%node
                print "Checking for sanity of node...."
                if node in self.MASTER:
                    print "Deleting ...\n%s\t%s"%(nodes,self.MASTER[nodes]['ip'])
                    self.manager.rm(nodes,force=True)
                    del self.MASTER[nodes]
                else:
                    print "%s is not a valid node, no such node is present in cluster"%node
                    continue
        self.file.writeFile(self.MASTER)
