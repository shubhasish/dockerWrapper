from config import getClient
import docker
from modules.fileFormatter import File
from config import WRAPPER_DB_PATH, DEPLOYMENT_FILE_PATH, API_DICT
from flask_restful import Resource
import pickledb
from flask import Response

class Manager(Resource):

    def template(self):
        self.file = File()
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH,False)
            self.SERVERS = self.db.get('servers')
            self.swarm = self.db.get('swarm')
        except Exception as e:
            pass


    def getMasterMachine(self):
        self.master = [x for x in self.SERVERS.keys() if self.SERVERS[x]['init']][0]
        print '\nMaster Node of this cluster: %s' % self.master
        self.masterMachine = getClient(self.master, self.SERVERS[self.master]['url'])


    # def deployTelegraf(self):
    #     kwargs = {'constraints':['node.role==manager'],'name':'telegraf','networks':['icarus'],'mounts':['~/telegraf.conf:/etc/telegraf/telegraf.conf','/var/run/docker.sock:/var/run/docker.sock']}
    #
    #     service = self.masterMachine.services.create(image=self.image,**kwargs)
    #     return service
    #
    #
    # def copyConfigFile(self):
    #     self.machine.scp(self.path,self.master+':~')
    #
    # def monitor(self,path):
    #     self.path = path
    #     print 'Copying telegraf configuration file'
    #     self.copyConfigFile()
    #     print '\n\nDeploying Telegraf as a service'
    #     service = self.deployTelegraf()
    #     print '\nTelegraf deployed as a service with id %s' % service.short_id
    #
    def post(self):
        print 'Post Received'
        self.template()

        if self.SERVERS == None:
            response = str({'status': 'failure', 'message': 'No servers found, Initialize a swarm cluster.'})
            return Response(response,mimetype='application/json')
        self.getMasterMachine()
        
        def deploy():
            yield 'Deploying Portainer\n\n'
            
            portainer = self.deployUI()

            if portainer['status'] == 'failure':
                yield str(portainer)
                return

            yield str(portainer)

        return Response(deploy(),mimetype='application/json')

    def deployUI(self):
        kwargs = {'name':'portainer','args':['-H','unix:///var/run/docker.sock'],'constraints':['node.role == manager'],'endpoint_spec':docker.types.EndpointSpec(mode='vip',ports={9000:9000}),'mounts':['//var/run/docker.sock://var/run/docker.sock']}
        try:
            portainer_service = self.masterMachine.services.create(image='portainer/portainer',**kwargs)
            return {'status': 'success', 'message': 'Service deployed successfully with service ID = %s'%portainer_service.id}
        except Exception as e:
            
            return {'status':'failure','message':str(e.message)}
