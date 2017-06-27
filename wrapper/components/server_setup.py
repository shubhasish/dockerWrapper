import os
import copy
from ..config import CONFIG_FORMATT
from ..modules.fileFormatter import File
from ..modules.dockerMachine import dockerMachine
from swarm_handler import Swarm_Handler
class Server:
    def __init__(self,path):
        self.MASTER = dict()
        self.file = File()
        try:
            print "Reading Configuration File"
            self.config_file = self.file.readFile('config.json')
        except Exception as e:
            print e
            print "Exiting Cluster Creation Process"
            os._exit(1)
        try:
            self.MASTER = self.file.readFile('shape.memory')
        except Exception as e:
            pass

    def get_cluster(self):
        return set(self.MASTER.keys())

    def get_requirement(self):
        return set(self.config_file.keys())

    def create_cluster(self):
        print "Getting machines to be created"
        self.required_nodes = self.get_requirement()
        print "Getting existing nodes in the cluster"
        self.existing_nodes = self.get_cluster()
        if len(self.existing_nodes) == 0:
            print "No existing nodes in the cluster"
            print "Following nodes will be created"
            for node in self.required_nodes:
                print "%s \t %s" % (node, self.config_file[node]['role'])
            print "Creating Nodes...."
            masterList = self.createNodes(self.required_nodes)
        else:
            print "Following nodes are present in the cluster"
            for node in self.existing_nodes:
                print "%s \t %s" % (node, self.existing_nodes[node]['role'])
            requirements = self.required_nodes.difference(self.existing_nodes)
            if len(requirements) > 0:
                print "Following nodes will be created"
                for node in requirements:
                    print "%s \t %s" % (node, self.config_file[node]['role'])
                masterList = self.createNodes(requirements)
            else:
                print "No new machines to be created"

    def createNodes(self,createList):
        docker = dockerMachine()
        master = []
        for node in createList:
            print "Creating %s...." % node
            docker.createMachine(name=node, driver=self.config_file[node]['driver'])
            config = CONFIG_FORMATT
            config['url'] = docker.getURL(node)
            config['ip'] = docker.getIp(node)
            config['role'] = self.config_file[node]['role']
            config['driver'] = self.config_file[node]['driver']
            if (self.config_file[node]['driver'] == "manager"):
                master.append((node,docker.getURL(node),docker.getIp(node)))
            self.MASTER[node] = copy.deepcopy(config)
        self.file.writeFile(self.MASTER)
        return master


