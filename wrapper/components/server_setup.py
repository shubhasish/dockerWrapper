import os
import copy
import pickledb
from config import CONFIG_FORMATT
from modules.fileFormatter import File
from modules.dockerMachine import dockerMachine
from swarm_handler import Swarm_Handler
from config import DM_URL
from modules.machine import Machine
from config import WRAPPER_DB_PATH
from config import dir_path
from flask_restful import Resource
from flask_restful import request


class Server(Resource):


    def get(self):
        return "Wrong Method, Use POST intead"

    def template(self):
        self.SERVERS = dict()
        self.file = File()
        self.manager = Machine(path=DM_URL)
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH, False)
            self.SERVERS = self.db.get('servers')
        except Exception as e:
            pass

    def post(self):
        self.template()
        serverDict = request.get_json()
        self.create_cluster(serverDict)

        return {x:self.SERVERS[x] for x in serverDict.keys()}

    def create_cluster(self,serverDict):
        print "\nGetting machines to be created"
        self.required_nodes = serverDict
        print "\nGetting existing nodes in the cluster"
        self.existing_nodes = self.SERVERS

        if self.existing_nodes and len(self.existing_nodes.keys())>0:
            print "Following nodes are present in the cluster"
            for node in self.existing_nodes:
                print "%s \t %s" % (node, self.existing_nodes[node]['role'])
            requirements = set(self.required_nodes.keys()).difference(set(self.existing_nodes.keys()))
            if len(requirements) > 0:
                print "Following nodes will be created"
                for node in requirements:
                    print "%s \t %s" % (node, self.required_nodes[node]['role'])
                try:
                    self.createNodes(requirements)
                except Exception as e:
                    print e
                finally:
                    self.db.dump()
            else:
                print "No new machines to be created"
        else:
            self.SERVERS = dict()
            print "No existing nodes in the cluster"
            print "\n\nFollowing nodes will be created"
            for node in self.required_nodes.keys():
                print "%s \t %s" % (node, self.required_nodes[node]['role'])

            try:
                self.createNodes(self.required_nodes.keys())
            except Exception as e:
                print e
            finally:
                self.db.dump()

    def createNodes(self,createList):
        docker = dockerMachine()

        for node in createList:
            print "\nCreating %s...." % node
            print self.required_nodes[node]
            self.manager.create(name=node, **self.required_nodes[node])
            #docker.createMachine(name=node, driver=self.config_file[node]['driver'])
            config = CONFIG_FORMATT
            config['url'] = docker.getURL(node)
            config['ip'] = docker.getIp(node)
            config['role'] = self.required_nodes[node]['role']
            config['driver'] = self.required_nodes[node]['driver']
            self.SERVERS[node] = copy.deepcopy(config)
            self.db.set('servers',self.SERVERS)



