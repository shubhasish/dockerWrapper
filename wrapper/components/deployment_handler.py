import docker
from copy import deepcopy
import yaml
from config import getClient
from config import WRAPPER_DB_PATH, DEPLOYMENT_FILE_PATH
from modules.fileFormatter import File
import os
import  time
from flask_restful import Resource, request
import pickledb
from flask import Response

class Deployment(Resource):
    def template(self):
        self.file = File()
        # self.STATE = None
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH,False)
            self.SERVERS = self.db.get('servers')
            self.swarm = self.db.get('swarm')
        except Exception as e:
            pass


        self.master = [x for x in self.SERVERS.keys() if self.SERVERS[x]['init']][0]
        print "\nMaster Node of this cluster: %s"%self.master
        self.masterMachine = getClient(self.master,self.SERVERS[self.master]['url'])
        self.serviceList = { x.name: x.id for x in self.listServices()}

    def helloWorld(self):
        print "Inside"
        yield "Hello World"
    def post(self):
        self.template()
        # postJson = request.get_json()
        file = request.files['deploymentFile']
        self.serviceName = request.form['serviceName']

        file.save(DEPLOYMENT_FILE_PATH + 'compose.yaml')
        # return "ok"
        # self.serviceName = postJson['serviceName']
        # self.services = postJson['contents']
        self.yml = yaml.load(open(DEPLOYMENT_FILE_PATH + 'compose.yaml', 'r+'))
        self.services = self.yml['services']
        # print "Befor Deploy"
        #
        # def helloWorld():
        #     print "Inside"
        #     yield "Hello World"
        # def deploy():
        #     print "Before function"
        #     helloWorld()
        #
        message = self.deployService()
        return {'message':message}
        # generator = deploy()
        # return Response(generator,mimetype='text/plain')


    def deployService(self):
        # self.yml = yaml.load(open(path, 'r+'))
        # self.services = self.yml['services']
        if self.serviceName == "all" or self.serviceName in self.services:
            pass
        else:
            return "Not a valid service name"
            #os._exit(1)

##------------------------------------------ Not necessary in version 2-----------------------------##

        # if "registry" in self.serviceList:
        #     print "\nRegistry already deployed, so skipping it"
        # else:
        #     print "\nDeploying local registry.."
        #     try:
        #         serviceId = self.createRegistry()
        #         print "\nService Deployed Successfully with service id: %s"%serviceId.id
        #     except Exception as e:
        #         print e
        #         print "\nRegistry not deployed, Custom built image may not work properly, so exiting program."
        #         os._exit(1)
        # if "portainer" in self.serviceList:
        #     print "\nPortainer already deployed, so skipping it"
        # else:
        #     print "\nDeploying Portainer.."
        #     try:
        #         serviceId = self.deployUI()
        #         print "\nService Deployed Successfully with service id: %s" % serviceId.id
        #     except Exception as e:
        #         print e
        #         print "\nPortainer not Deployed. UI may not be available."

        ### Create an Overlay Network
        self.network = self.createNetwork()
        servicesDict = self.getServicesList()
        for service in servicesDict.keys():
            try:
                self.createService(servicesDict[service])
            except Exception as e:
                return e.message
        return "All Services Deployed Successfully"

##---------------------------------------------- Separate API for build ----------------------------#
        #     if "build" in servicesDict[service]:
        #         servicesDict[service]['build']['tag'] = "127.0.0.1:5000/%s"%servicesDict[service]['image']
        #         servicesDict[service]['build']['stream'] = True
        #         image = self.imageBuilder(**servicesDict[service]['build'])
        #         self.pushImageToRegistry(servicesDict[service]['build']['tag'])
        #
        #         servicesDict[service]['image'] = servicesDict[service]['build']['tag']
        #         del servicesDict[service]['build']
        #         self.createService(servicesDict[service])
        #     else:
        #         self.createService(servicesDict[service])

    def reDeploy(self,path,serviceName):
        self.yml = yaml.load(open(path, 'r+'))
        self.services = self.yml['services']
        if serviceName == "all" or serviceName in self.services:
            pass
        else:
            print "Not a valid service name"
            os._exit(1)
        servicesDict = self.getServicesList()
        dict = {}
        for service in servicesDict.keys():
            serviceId = self.createService(servicesDict[service])
            dict[service] = serviceId
        return dict

#--------------------------- No more need of removal and re-deploy. Use the separate APi ------------
            # print "Removing Service %s" % service
            # self.serviceRemover(service)
            # if "build" in servicesDict[service]:
            #     servicesDict[service]['build']['tag'] = "127.0.0.1:5000/%s"%servicesDict[service]['image']
            #     print "Removing any previous images"
            #     time.sleep(10)
            #     self.imageCleaner(servicesDict[service]['build']['tag'])
            #     servicesDict[service]['build']['stream'] = True
            #     print "Building Image"
            #     image = self.imageBuilder(**servicesDict[service]['build'])
            #     print "Pushing Image to Local Registry"
            #     self.pushImageToRegistry(servicesDict[service]['build']['tag'])
            #
            #     servicesDict[service]['image'] = servicesDict[service]['build']['tag']
            #     del servicesDict[service]['build']
            #
            #     print "Creating Service"
            #     self.createService(servicesDict[service])
            # else:
            #     print "Creating Service"
            #     self.createService(servicesDict[service])


#----------------------------------------------------------------------------
    def deployUI(self):
        kwargs = {"name":"portainer","args":["-H","unix:///var/run/docker.sock"],"constraints":["node.role == manager"],"endpoint_spec":docker.types.EndpointSpec(mode='vip',ports={9000:9000}),"mounts":["//var/run/docker.sock://var/run/docker.sock"]}
        try:
            portainer_service = self.masterMachine.services.create(image="portainer/portainer",**kwargs)
            return portainer_service
        except Exception as e:
            return e

    def createRegistry(self):
        kwargs = {"name": "registry","endpoint_spec": docker.types.EndpointSpec(mode='vip', ports={5000: 5000})}
        registry_service = self.masterMachine.services.create(image ="registry:2",**kwargs)
        return registry_service


#-----------------------------------------------------------
    def listServices(self):
        return self.masterMachine.services.list()

    def serviceFinder(self,serviceName):
        serviceList = self.listServices()
        return [x for x in serviceList if x.name == serviceName][0]

    def serviceRemover(self,serviceName):
        service = self.serviceFinder(serviceName)
        service.remove()

    def createService(self,dict):
        # if 'network' in dict:
        #     dict['networks'].append('icarus')
        # else:
        #     dict['networks'] = ['icarus']
        image = dict.pop('image')
        if 'build' in dict:
            dict.pop('build')
        command = None
        if "command" in dict:
            command = dict.pop('command')
        serviceId = self.masterMachine.services.create(image=image,command=command,**dict)
        print "\nService Deployed Successfully with service id: %s" % serviceId.id
        return serviceId

    def createNetwork(self):
        networks = [x.name for x in self.masterMachine.networks.list()]
        if 'icarus' in networks:
            pass
        else:
            network = self.masterMachine.networks.create('icarus',driver="overlay")
        return None

#------------------------------------------------------------------

    def imageBuilder(self,**kwargs):
        image = self.masterMachine.images.build(**kwargs)
        return image

    def pushImageToRegistry(self,image):
        self.masterMachine.images.push(image,**{'stream':True})

    def imageCleaner(self,image):
        self.masterMachine.images.remove(image=image)
#-----------------------------------------------------------------



    def getServicesList(self):
        serviceDict = {}
        if self.serviceName == 'all':
            for service in self.services.keys():
                deployOptions = self.getOptions(self.services[service])
                deployOptions['name'] = service
                serviceDict[service] = deepcopy(deployOptions)
        else:
            deployOptions = self.getOptions(self.services[self.serviceName])
            deployOptions['name'] = self.serviceName
            serviceDict[self.serviceName] = deepcopy(deployOptions)
        return serviceDict


    def getOptions(self,service):
        kwargs = {}

        options = service
        for option in options.keys():
            if option == "build":
                arguments = self.getBuildDetails(options[option])
                kwargs['build'] = arguments

            elif option == "image":
                kwargs['image'] = (options['image'])
            elif option == "command":
                kwargs['command'] = (options['command'])

            elif option == "labels":
                if type(options['labels']) == dict:
                    kwargs['container_labels'] = (options['labels'])
                else:
                    kwargs['container_labels'] = (
                    {(x.split('=')[0]): (x.split('=')[1] if '=' in x else None) for x in options['labels']})



            elif option == "deploy":
                serviceMode = {'mode': 'replicated', 'replicas': 1}
                if "mode" in options['deploy']:
                    serviceMode['mode'] = options['deploy']['mode']
                if "replicas" in options['deploy']:
                    serviceMode['mode'] = options['deploy']['replicas']
                kwargs['mode'] = (docker.types.ServiceMode(mode=serviceMode['mode'], replicas=serviceMode['replicas']))
                if "placement" in options['deploy']:
                    kwargs['constraints'] = (options['deploy']['placement']['constraints'])
                if "update_config" in options['deploy']:
                    configurationDict = self.getUpdateConfig(options['deploy']['update_config'])
                    kwargs['update_config'] = (docker.types.UpdateConfig(parallelism=configurationDict['parallelism'],
                                                                         delay=configurationDict['delay'],
                                                                         failure_action='continue',
                                                                         monitor=configurationDict['monitor'],
                                                                         max_failure_ratio=configurationDict[
                                                                             'max_failure_ratio']))
                if "resources" in options['deploy']:
                    resourceDict = self.getResources(options['deploy']['resources'])
                    kwargs['resources'] = (
                    docker.types.Resources(cpu_limit=resourceDict['cpu_limit'], mem_limit=resourceDict['mem_limit'],
                                           cpu_reservation=resourceDict['cpu_reservation'],
                                           mem_reservation=resourceDict['mem_reservation']))
                if "restart_policy" in options['deploy']:
                    policyDict = self.getRestartPolicy(options['deploy']['restart_policy'])
                    kwargs['restart_policy'] = (
                    docker.types.RestartPolicy(condition=policyDict['condition'], delay=policyDict['delay'],
                                               max_attempts=policyDict['max_attempts'], window=policyDict['window']))


            elif option == "depends_on":
                depends_on = options['depends_on']
                kwargs['depends'] = depends_on

            elif option == "env_file":
                pass
            elif option == "environment":
                if type(options['environment']) == dict:
                    envList = []
                    for x in options['environment']:
                        if options['environment'][x] != None:
                            envList.append('%s=%s' % (x, options['environment'][x]))
                        else:
                            envList.append(x)
                    kwargs['env'] = (envList)
                else:
                    kwargs['env'] = options['environment']

            elif option == "logging":
                kwargs['log_driver'] = options['logging']['driver']
                kwargs['log_driver_options'] = options['logging']['options']
            elif option == "networks":
                kwargs['networks'] = options['networks']
            elif option == "ports":
                ports = dict()
                for port in options['ports']:
                    if '/' in port:
                        protocol = port.rsplit('/')[1]
                        port = port.rsplit('/')[0]
                        ports[int(port.rsplit(':', 1)[1])] = (int(port.rsplit(':', 1)[0]), protocol)
                    elif ':' not in port:
                        ports[port] = port
                    else:
                        ports[int(port.rsplit(':', 1)[1])] = int(port.rsplit(':', 1)[0])

                kwargs['endpoint_spec'] = docker.types.EndpointSpec(mode='vip', ports=ports)
            elif option == "volumes":
                kwargs['mounts'] = options['volumes']
            elif option == "secrets":
                kwargs['secrets'] = options['secrets']

            elif option == "hostname":
                kwargs['hostname'] = options['hostname']
            elif option == "user":
                kwargs['user'] = options['user']
            elif option == "working_dir":
                kwargs['workdir'] = options['working_dir']

        return kwargs



    def getBuildDetails(self,buildObject):
        build_args = dict()
        if type(buildObject) == dict:

            if "context" in buildObject:
                build_args['path'] = (buildObject['context'])
            else:
                print "Please provide with the build context path by mentioning 'context' under build tag"
            if "dockerfile" in buildObject:
                build_args['dockerfile'] = (buildObject["dockerfile"])
            if "args" in buildObject:
                build_args['args'] = (buildObject["args"])
            if "cache_form" in buildObject:
                build_args['cache_from'] = (buildObject['cache_from'])
            else:
                "Enter a correct docker compose file options,Please check docker compose documentation for more details"
        else:
            build_args['path'] = (buildObject['build'])
            build_args['dockerfile'] = ("Dockerfile")
        return build_args

    def getUpdateConfig(self,dict):
        configDict = {'parallelism': None, 'delay': None, 'failure_action': None, 'monitor': None,
                      'max_failure_ratio': None}
        if 'parallelism' in dict:
            configDict['parallelism'] = dict['parallelism']
        if 'delay' in dict:
            configDict['delay'] = dict['delay']
        if 'failure_action' in dict:
            configDict['failure_action'] = dict['failure_action']
        if 'monitor' in dict:
            configDict['monitor'] = dict['monitor']
        if 'max_failure_ratio' in dict:
            configDict['max_failure_ratio'] = dict['max_failure_ratio']
        return configDict

    def getResources(self,dict):
        resourceDict = {'cpu_limit': None, 'mem_limit': None, 'cpu_reservation': None, 'mem_reservation': None}
        if 'limits' in dict:
            if 'cpus' in dict['limits']:
                resourceDict['cpu_limit'] = dict['limits']['cpus']
            if 'memory' in dict['limits']:
                resourceDict['mem_limit'] = dict['limits']['cpus']
        if 'reservations' in dict:
            if 'cpus' in dict['reservations']:
                resourceDict['cpu_reservation'] = dict['limits']['cpus']
            if 'memory' in dict['reservations']:
                resourceDict['mem_reservation'] = dict['limits']['memory']
        return resourceDict

    def getRestartPolicy(self,dict):
        rPolicyDict = {'condition':'none', 'delay': 0, 'max_attempts': 0, 'window': 0}
        if 'condition' in dict:
            rPolicyDict['condition'] = dict['condition']
        if 'delay' in dict:
            rPolicyDict['delay'] = dict['delay']
        if 'max_attempts' in dict:
            rPolicyDict['max_attempts'] = dict['max_attempts']
        if 'window' in dict:
            rPolicyDict['window'] = dict['window']
        return rPolicyDict
