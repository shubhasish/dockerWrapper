from modules.swarm import Swarm
from modules.fileFormatter import File
from copy import deepcopy
from threading import Thread
from config import DM_URL
from config import WRAPPER_DB_PATH

from modules.machine import Machine
import os
from flask_restful import Resource
from flask_restful import request
import pickledb

cmdJson={"join-token_manager":"sudo docker swarm join-token manager",
         "join-token_worker":"sudo docker swarm join-token worker"}

class Swarm_Handler(Resource):
    def get(self):
        return "Wrong method, Use POST instead"

    def post(self):
        self.template()
        swarmName = request.get_json()['swarm']

        message = self.checkNswarm(swarmName)

        return {'message':message}


    def template(self):
        self.SERVERS = dict()
        self.file = File()
        self.masterSet= set()
        self.slaveSet = set()
        self.init = False
        self.mainMaster = None
        self.swarmList = set()
        self.manager = Machine(path=DM_URL)
        try:

            self.db = pickledb.load(WRAPPER_DB_PATH,False)

            self.SERVERS = self.db.get('servers')
            self.swarm = self.db.get('swarm')
        except Exception as e:
            print e
            pass

        # try:
        #     print "Reading Configuration File"
        #     self.config_file = self.file.readFile('config.json')
        # except Exception as e:
        #     print e
        #     print "Exiting Cluster Creation Process"
        #     os._exit(1)
        # try:
        #     print "Reading state file for swarmCheck "
        #     self.SERVERS = self.file.readFile('shape.memory')
        # except Exception as e:
        #
        #     pass

    def checkNswarm(self,swarmName):

        self.db.set('swarm',swarmName)

        for server in self.SERVERS.keys():
            if self.SERVERS[server]['role'].lower() == "manager":
                if self.SERVERS[server]['swarm']:

                    self.swarmList.add(server)
                    if self.SERVERS[server]['init']:
                        self.init = True
                        self.mainMaster = server
                else:
                    self.masterSet.add(server)
            else:
                if self.SERVERS[server]['swarm']:
                    self.swarmList.add(server)
                else:
                    self.slaveSet.add(server)
        self.db.set('Master',list(self.masterSet))
        # print self.swarmList
        if len(self.swarmList) > 0:
            print "Swarm has already been initialized with %s"%self.mainMaster
            print "Following Nodes are in swarm:"
            for node in self.swarmList:
                print "%s \t %s" % (node, self.SERVERS[node]['role'])
            if len(self.masterSet) > 0 or len(self.slaveSet) > 0:
                print "Following new nodes will be added to the swarm cluster:"
                print "Masters:"
                for node in self.masterSet:
                    print "%s \t %s" % (node, self.SERVERS[node]['ip'])
                print "Slaves:"
                for node in self.slaveSet:
                    print "%s \t %s" % (node, self.SERVERS[node]['ip'])
                print "Obtaining join tokens for swarm....."
                joinTokens = self.getJoinToken(self.mainMaster)
                print "Joining swarm....."
                masterThread = Thread(target=self.swarm_join, args=(self.masterSet, joinTokens[0], self.mainMaster,))
                slaveThread = Thread(target=self.swarm_join, args=(self.slaveSet, joinTokens[1], self.mainMaster,))
                masterThread.start()
                slaveThread.start()
                masterThread.join()
                slaveThread.join()
                print "Swarm Cluster created Successfully"
                return "Swarm Cluster created Successfully"
            else:
                print "No new nodes to be added to the swarm cluster"
                return "No new nodes to be added to the swarm cluster"
        else:
            print "Swarm hasn't been initialized."
            print "Following new nodes will be added to the swarm cluster:"
            print "Masters:"
            for node in self.masterSet:
                print "%s \t %s" % (node, self.SERVERS[node]['ip'])
            print "Slaves:"
            for node in self.slaveSet:
                print "%s \t %s" % (node, self.SERVERS[node]['ip'])
            print "Initializing swarm....."
            self.mainMaster = self.masterSet.pop()
            try:
                joinTokens = self.swarm_init(self.mainMaster)
            except Exception as e:
                print e
            finally:
                self.db.set('servers',self.SERVERS)
                self.db.dump()
            print "Joining Swarm....."

            masterThread = Thread(target=self.swarm_join,args=(self.masterSet,joinTokens[0],self.mainMaster,))
            slaveThread = Thread(target=self.swarm_join,args=(self.slaveSet,joinTokens[1],self.mainMaster,))
            masterThread.start()
            slaveThread.start()
            masterThread.join()
            slaveThread.join()

            print "Swarm Cluster created Successfully"
            return "Swarm Cluster created Successfully"



    def create_swarm(self,swarmlist,dict):
        pass

    def swarm_init(self,master):
        swarmMaster = Swarm(name=master, url=self.SERVERS[master]['url'])
        swarmMaster.swarmInit(advertise_addr=self.SERVERS[master]['ip'])
        self.SERVERS[master]['swarm'] = deepcopy(True)
        self.SERVERS[master]['init'] = deepcopy(True)
        return self.getJoinToken(master)

    def swarm_join(self,nodeList,token,mainMaster):
        for node in nodeList:
            swarm = Swarm(name=node, url=self.SERVERS[node]['url'])
            try:
                ip = self.SERVERS[mainMaster]['ip'] + ':2377'

                listen = None
                if self.SERVERS[node]['role'] == "slave":
                    listen = self.SERVERS[node]['ip'] + ':2378'
                print "Joining %s \t %s"%(node,self.SERVERS[node]['ip'])
                swarm.joinSwarm(ip=ip,token=token,listen=listen)
                self.SERVERS[node]['swarm'] = deepcopy(True)
            except Exception as e:
                print e
                os._exit(1)
            finally:
                self.db.set('servers',self.SERVERS)
                self.db.dump()

    def getJoinToken(self,master):
        masterDetails = self.checkSwarm(master)
        if masterDetails[0]:
            managerToken = [x for x in masterDetails[1] if 'SWMTKN' in x][0]
            workerToken = [x for x in masterDetails[2] if 'SWMTKN' in x][0]
            return (managerToken,workerToken)
        else:
            print masterDetails[1]

    
    def checkSwarm(self,name):
        try:
            managerToken = self.manager.ssh(name,cmd=cmdJson['join-token_manager'],logging=False)
            workerToken = self.manager.ssh(name,cmd=cmdJson['join-token_worker'],logging=False)
            return (True,managerToken,workerToken)
        except Exception as e:
            return (False,e.message)
