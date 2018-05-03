import os
import sys
import pickledb
from modules.fileFormatter import File
from config import DM_URL
from config import dir_path
from config import WRAPPER_DB_PATH
from modules.machine import Machine
from flask_restful import request,Resource
from flask import Response

import logging

logging.basicConfig(format='%(levelname)s: %(message)s',stream=sys.stdout, level=logging.INFO)


class RemovalManager(Resource):

    def __init__(self):
        self.SERVERS = dict()
        self.file = File()
        self.manager = Machine(path=DM_URL)
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH,False)
            self.SERVERS = self.db.get("servers")
        except Exception as e:
            #pass
            pass

    def removeNodes(self,node):
        if not self.SERVERS:
            return "Check if you have already initialized cluster"

        if node=="all":
            logging.info("All nodes will  be deleted, and the workspace will be reseted.")
            for nodes in self.SERVERS.keys():
                logging.info("Deleting ...\n%s\t%s" % (nodes, self.SERVERS[nodes]["ip"]))
                self.manager.rm(nodes, force=True)
            os.remove(WRAPPER_DB_PATH)
            return "Whole cluster is deleted"
        else:
            logging.info("%s will be deleted"%node)
            logging.info("Checking for sanity of node....")
            if node in self.SERVERS:
                logging.info("Deleting ...\n%s\t%s"%(node,self.SERVERS[node]["ip"]))
                self.manager.rm(node,force=True)
                del self.SERVERS[node]
                self.db.set("servers",self.SERVERS)
            else:
                logging.error("No such node is present in cluster")

            self.db.dump()
        return "Selected nodes deleted"

