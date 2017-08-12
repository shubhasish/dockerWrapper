from config import getClient
from modules.machine import Machine
from config import DM_URL
import os
from modules.fileFormatter import File
from flask_restful import Resource

class Monitoring(Resource):

    def __init__(self):

        self.file = File()
        try:
            print "Reading state file for deployment\n "
            self.STATE = self.file.readFile('shape.memory')
        except Exception as e:
            print e
            os._exit(1)

        self.master = [x for x in self.STATE.keys() if self.STATE[x]['init']][0]
        print "\nMaster Node of this cluster: %s" % self.master
        self.masterMachine = getClient(self.master, self.STATE[self.master]['url'])
        self.image = "telegraf:alpine"

        self.machine = Machine(DM_URL)

    def deployTelegraf(self):
        kwargs = {"constraints":["node.role==manager"],"name":"telegraf","networks":["icarus"],"mounts":["~/telegraf.conf:/etc/telegraf/telegraf.conf","/var/run/docker.sock:/var/run/docker.sock"]}

        service = self.masterMachine.services.create(image=self.image,**kwargs)
        return service


    def copyConfigFile(self):
        self.machine.scp(self.path,self.master+':~')

    def monitor(self,path):
        self.path = path
        print "Copying telegraf configuration file"
        self.copyConfigFile()
        print "\n\nDeploying Telegraf as a service"
        service = self.deployTelegraf()
        print "\nTelegraf deployed as a service with id %s" % service.short_id

    def deployUI(self):
        kwargs = {"name":"portainer","args":["-H","unix:///var/run/docker.sock"],"constraints":["node.role == manager"],"endpoint_spec":docker.types.EndpointSpec(mode='vip',ports={9000:9000}),"mounts":["//var/run/docker.sock://var/run/docker.sock"]}
        try:
            portainer_service = self.masterMachine.services.create(image="portainer/portainer",**kwargs)
            return portainer_service
        except Exception as e:
            return e
