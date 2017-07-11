import os
import pickledb
from modules.fileFormatter import File
from config import DM_URL
from config import dir_path
from config import WRAPPER_DB_PATH
from modules.machine import Machine
from flask_restful import request,Resource

class RemovalManager(Resource):

    def get(self):
        return "Wrong method, Use POST instead"

    def post(self):
        option = request.get_json()['option']
        response = self.removeNodes(option)
        return {'message':response}

    def __init__(self):
        self.SERVERS = dict()
        self.file = File()
        self.manager = Machine(path=DM_URL)
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH,False)
            self.SERVERS = self.db.get('servers')
        except Exception as e:
            pass
            #print "\n Check if you have already initialized cluster in this folder...."

    def removeNodes(self,nodes=["all"]):
        if "all" in nodes:
            print "All nodes will  be deleted, and the workspace will be reseted."
            for nodes in self.SERVERS.keys():
                print "Deleting ...\n%s\t%s" % (nodes, self.SERVERS[nodes]['ip'])
                self.manager.rm(nodes, force=True)
            os.remove(dir_path + "/wrapper.db")
            return "Whole cluster is deleted"
        for node in nodes:
            print "%s will be deleted"%node
            print "Checking for sanity of node...."
            if node in self.SERVERS:
                print "Deleting ...\n%s\t%s"%(nodes,self.SERVERS[nodes]['ip'])
                self.manager.rm(nodes,force=True)
                del self.SERVERS[nodes]
                self.db.set('servers',self.SERVERS)
            else:
                print "%s is not a valid node, no such node is present in cluster"%node
                continue
            self.db.dump()
        return "Selected nodes deleted"

