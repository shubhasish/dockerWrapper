import os
import copy
from config import CONFIG_FORMATT
from modules.fileFormatter import File
from modules.dockerMachine import dockerMachine
from swarm_handler import Swarm_Handler
from config import DM_URL
from modules.machine import Machine
from config import dir_path


class Server:
    def __init__(self,path=dir_path+"/config.json"):
        self.MASTER = dict()
        self.file = File()
        self.manager = Machine(path=DM_URL)
        try:
            print "Reading Configuration File"
            self.config_file = self.file.readFile(path)
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
        masterList=[]
        print "\nGetting machines to be created"
        self.required_nodes = self.get_requirement()
        print "\nGetting existing nodes in the cluster"
        self.existing_nodes = self.get_cluster()
        if len(self.existing_nodes) == 0:
            print "No existing nodes in the cluster"
            print "\n\nFollowing nodes will be created"
            for node in self.required_nodes:
                print "%s \t %s" % (node, self.config_file[node]['role'])

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
        swarm = Swarm_Handler()
        swarm.checkNswarm()
        return masterList

    def createNodes(self,createList):
        docker = dockerMachine()
        master = []
        for node in createList:
            print "\nCreating %s...." % node
            self.manager.create(name=node, driver=self.config_file[node]['driver'])
            #docker.createMachine(name=node, driver=self.config_file[node]['driver'])
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


