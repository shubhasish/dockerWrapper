import docker
from copy import deepcopy
import yaml
from config import getClient
from config import WRAPPER_DB_PATH, DEPLOYMENT_FILE_PATH, API_DICT
from modules.fileFormatter import File
import os
from flask_restful import Resource, request
import pickledb
from service_handler import RemoveService
from flask import Response
import requests

class Deployment(Resource):
    def template(self):
        self.file = File()
        self.host = 'localhost'
        self.port = 5000

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


    def post(self):
        print "Post Received"
        self.template()

        file = request.files['deploymentFile']
        file.save(DEPLOYMENT_FILE_PATH + 'compose.yaml')

        self.serviceName = request.form['serviceName']
        print "Starting to Deploy %s component"%self.serviceName
        self.yml = yaml.load(open(DEPLOYMENT_FILE_PATH + 'compose.yaml', 'r+'))
        self.services = self.yml['services']

        message = self.deployService()
        return {'status':message[0],'message':message[1]}


    def deployService(self):
        if self.serviceName == "all" or self.serviceName in self.services:
            pass
        else:
            return "Not a valid service name"

        print "Preparing services for deployment"
        servicesDict = self.getServicesList()

        print "Deploying Services"
        for service in servicesDict.keys():
            print "Deploying Service %s"%service
            try:
                self.serviceRemover(service)
            except Exception as e:
                return ('Failure',str(e.message))

            try:
                self.createService(servicesDict[service])
            except Exception as e:
                return ('failure',str(e.message))
        return ('Success',"All Services Deployed Successfully")


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



#-----------------------------------------------------------
    def listServices(self):
        return self.masterMachine.services.list()

    def serviceFinder(self,serviceName):
        serviceList = self.listServices()
        return [x for x in serviceList if x.name == serviceName][0]

    def serviceRemover(self,serviceName):
        service_remover = RemoveService()
        response = service_remover.deleteService(serviceName)
        return response

    def createService(self,dict):
        ### Command to remove service


        #### Create Servcie

        image = dict.pop('image')
        if 'build' in dict:
            dict.pop('build')
        command = None
        if "command" in dict:
            command = dict.pop('command')
        serviceId = self.masterMachine.services.create(image=image,command=command,**dict)
        print "\nService Deployed Successfully with service id: %s" % serviceId.id
        return serviceId

    # def createNetwork(self):
    #     networks = [x.name for x in self.masterMachine.networks.list()]
    #     if 'icarus' in networks:
    #         pass
    #     else:
    #         network = self.masterMachine.networks.create('icarus',driver="overlay")
    #     return None


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
