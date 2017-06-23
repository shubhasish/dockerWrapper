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
            self.config_file = self.file.readFile('config.json')
        except Exception as e:
            print e
            os._exit(1)
        try:
            self.state_file = self.file.readFile('shape.memory')
        except Exception as e:
            pass

    def get_cluster(self):
        return set(self.state_file.keys())

    def get_requirement(self):
        return set(self.config_file.keys())

    def create_cluster(self):
        self.required_machines = self.get_requirement()
        self.existing_cluster = self.get_cluster()
        if len(self.existing_cluster) == 0:
            print "No nodes are present in this cluster"
            print "Following nodes will be created"
            for node in self.required_machines:
                print "%s \t %s" % (node, self.config_file[node]['role'])
            masterList = self.createMachines(self.required_machines)

            swarmHandler = Swarm_Handler()

            swarmHandler.swarm_init(masterList[0])
        else:
            print "Following nodes are present in the cluster"
            for node in self.existing_cluster:
                print "%s \t %s" % (node, self.existing_cluster[node]['role'])
            self.createMachines(self.required_machines.difference(self.existing_cluster))

    def createMachines(self,createList):
        docker = dockerMachine()
        master = []
        if len(createList) > 0:
            print "Following nodes will be created"

            for node in createList:
                print "Creating the node %s" % node
                docker.createMachine(name=node, driver=self.config_file[node]['driver'])
                config = CONFIG_FORMATT
                config['url'] = docker.getURL(node)
                config['ip'] = docker.getIp(node)
                config['role'] = self.config_file[node]['role']
                config['driver'] = self.config_file[node]['driver']
                if (self.config_file[node]['driver'] == "manager"):
                    master.append((node,docker.getURL(node),docker.getIp(node)))
                self.MASTER[node] = copy.deepcopy(config)
            return master
        else:
            print "No new machines to be created"
            return master

