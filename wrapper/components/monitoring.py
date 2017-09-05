from config import getClient, dir_path
from modules.machine import Machine
from config import DM_URL, WRAPPER_DB_PATH
import pickledb
import docker
from modules.fileFormatter import File
from flask_restful import Resource
from flask import request, Response

class Monitoring(Resource):

    def template(self):

        self.file = File()
        self.SERVERS = None
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH, False)
            self.SERVERS = self.db.get('servers')
        except Exception as e:
            pass

    def getMachines(self):
        self.master = [x for x in self.SERVERS.keys() if self.SERVERS[x]['init']][0]
        print '\nMaster Node of this cluster: %s' % self.master
        self.masterMachine = getClient(self.master, self.SERVERS[self.master]['url'])
        self.image = "telegraf:alpine"

        self.machine = Machine(DM_URL)

    def deployTelegraf(self):
        servicemode = (docker.types.ServiceMode(mode='global'))

        kwargs = {"mode":servicemode,"name":"telegraf","mounts":["/home/docker/telegraf.conf:/etc/telegraf/telegraf.conf","/var/run/docker.sock:/var/run/docker.sock"],"networks":["icarus"]}

        try:
            service = self.masterMachine.services.create(image=self.image,**kwargs)
            return str({'status':'success','message':'Service deployed successfully with id %s'%service.id})
        except Exception as e:
            print e
            return str({'status':'failure','message':str(e.message)})



    def copyConfigFile(self,server):
        self.machine.scp('telegraf.conf',server+":~")


    def post(self):
        data = request.get_json()

        influxDb = data['influxDB']

        #telegraf_conf = open(dir_path+'/telegraf.txt','r+')

        # telegraf_conf = (telegraf_conf.read()).replace('$$influxdb$$',str(influxDb))
        #
        # file = open('telegraf.conf','w+')
        #
        # file.write(telegraf_conf)
        # file.close()
        self.template()
        if self.SERVERS == None:
            response = str({'status': 'failure', 'message': 'No servers found, Initialize a swarm cluster.'})
            return Response(response,mimetype='application/json')

        self.getMachines()

        def deploy(servers,influxDb):
            yield "Transfering Telegraf Config files to target servers\n\n"
            print "transfering Files"
            for server in servers:
                yield "Copying Config file to the servers %s\n\n"%server
                conf = open(dir_path + '/telegraf.txt', 'r+')
                test = conf.read()
                test = test.replace('$$influxdb$$', str(influxDb))
                test = test.replace('$$HOSTNAME$$',str(server))

                file = open('telegraf.conf', 'w+')

                file.write(test)
                file.close()
                try:
                    self.copyConfigFile(server)
                except Exception as e:
                    print e
            yield "Starting Telegraf Service\n\n"

            telegraf = self.deployTelegraf()
            yield telegraf
        return Response(deploy(self.SERVERS,influxDb),mimetype='application/json')




    # def deployUI(self):
    #     kwargs = {"name":"portainer","args":["-H","unix:///var/run/docker.sock"],"constraints":["node.role == manager"],"endpoint_spec":docker.types.EndpointSpec(mode="vip",ports={9000:9000}),"mounts":["//var/run/docker.sock://var/run/docker.sock"]}
    #     try:
    #         portainer_service = self.masterMachine.services.create(image="portainer/portainer",**kwargs)
    #         return portainer_service
    #     except Exception as e:
    #         return e
