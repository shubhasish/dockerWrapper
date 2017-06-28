from modules.swarm import Swarm
from modules.dockerMachine import dockerMachine
from modules.fileFormatter import File
from copy import deepcopy
from threading import Thread
import os
class Swarm_Handler:

    def __init__(self):
        self.STATE = dict()
        self.file = File()
        self.masterSet= set()
        self.slaveSet = set()
        self.init = False
        self.mainMaster = None
        self.swarmList = set()
        # try:
        #     print "Reading Configuration File"
        #     self.config_file = self.file.readFile('config.json')
        # except Exception as e:
        #     print e
        #     print "Exiting Cluster Creation Process"
        #     os._exit(1)
        try:
            print "Reading state file for "
            self.STATE = self.file.readFile('shape.memory')
        except Exception as e:
            pass

        self.dockerMachine = dockerMachine()

    def checkNswarm(self):
        for node in self.STATE.keys():
            if self.STATE[node]['role'].lower() == "master":
                if self.STATE[node]['swarm']:
                    self.swarmList.add(node)
                    if self.STATE[node]['init']:
                        self.init = True
                        self.mainMaster = node
                else:
                    self.masterSet.add(node)
            else:
                if self.STATE[node]['swarm']:
                    self.swarmList.add(node)
                else:
                    self.slaveSet.add(node)
        if len(self.swarmList) > 0:
            print "Swarm has already been initialized with %s"%self.mainMaster
            print "Following Nodes are in swarm:"
            for node in self.swarmList:
                print "%s \t %s" % (node, self.STATE[node]['role'])
            if len(self.masterSet) > 0 or len(self.slaveSet) > 0:
                print "Following new nodes will be added to the swarm cluster:"
                print "Masters:"
                for node in self.masterSet:
                    print "%s \t %s" % (node, self.STATE[node]['ip'])
                print "Slaves:"
                for node in self.slaveSet:
                    print "%s \t %s" % (node, self.STATE[node]['ip'])
                print "Obtaining join tokens for swarm....."
                joinTokens = self.getJoinToken(self.mainMaster)
                print "Joining swarm....."
                masterThread = Thread(target=self.swarm_join, args=(self.masterSet, joinTokens[0], self.mainMaster,))
                slaveThread = Thread(target=self.swarm_join, args=(self.slaveSet, joinTokens[0], self.mainMaster,))
                masterThread.start()
                slaveThread.start()
                masterThread.join()
                slaveThread.join()
                self.file.writeFile(self.STATE)

            else:
                print "No new nodes to be added to the swarm cluster."
        else:
            print "Swarm hasn't been initialized."
            print "Following new nodes will be added to the swarm cluster:"
            print "Masters:"
            for node in self.masterSet:
                print "%s \t %s" % (node, self.STATE[node]['ip'])
            print "Slaves:"
            for node in self.slaveSet:
                print "%s \t %s" % (node, self.STATE[node]['ip'])
            print "Initializing swarm....."
            self.mainMaster = self.masterSet.pop()
            joinTokens = self.swarm_init(self.mainMaster)
            print "Joining Swarm....."
            masterThread = Thread(target=self.swarm_join,args=(self.masterSet,joinTokens[0],self.mainMaster,))
            slaveThread = Thread(target=self.swarm_join,args=(self.slaveSet,joinTokens[0],self.mainMaster,))
            masterThread.start()
            slaveThread.start()
            masterThread.join()
            slaveThread.join()
            self.file.writeFile(self.STATE)


    def create_swarm(self,swarmlist,dict):
        pass

    def swarm_init(self,master):
        swarmMaster = Swarm(name=master, url=self.STATE[master]['url'])
        swarmMaster.swarmInit(advertise_addr=self.STATE[master]['ip'])
        self.STATE[master]['swarm'] = deepcopy(True)
        self.STATE[master]['init'] = deepcopy(True)
        return self.getJoinToken(master)

    def swarm_join(self,nodeList,token,mainMaster):
        for node in nodeList:
            swarm = Swarm(name=node, url=self.STATE[node]['url'])
            try:
                print "Joining %s \t %s"%(node,self.STATE[node]['ip'])
                swarm.joinSwarm(ip=self.STATE[mainMaster]['ip'],token=token,listen=self.STATE[node]['ip'])
                self.STATE[node]['swarm'] = deepcopy(True)
            except Exception as e:
                print e
                os._exit(1)
    def getJoinToken(self,master):
        masterDetails = self.dockerMachine.checkSwarm(master)
        managerToken = [x for x in masterDetails[1] if 'SWMTKN' in x][0]
        workerToken = [x for x in masterDetails[2] if 'SWMTKN' in x][0]
        return (managerToken,workerToken)
