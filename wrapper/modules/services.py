from tls import TLS
import docker
import yaml
from copy import deepcopy


class Services:

    def __init__(self,deploymentFile='../composer/docker-compose.yml'):#,name,url,deploymentFile='../composer/docker-compose.yml'):

################### Variables......
        self.build = ""
        self.context = ""
        self.dockerFile = ""
        self.buildArgs = dict()
########### Initialization
        tls = TLS()
        # self.tlsConfig = tls.getTLSconfig(name)
        self.stream = open(deploymentFile, 'r')
        # self.client = docker.DockerClient(base_url=url, tls=self.tlsConfig)

    def listServices(self):
        return self.client.services.list()

    def getServicesList(self):
        services =  yaml.load(self.stream)['services']

        for service in services:
            kwargs = {}
            self.name = service
            options = services[service]
            for option in options.keys():
                if option == "build":
                    build_args = dict()
                    if type(options[option]) == dict:

                        if "context" in options["build"]:
                            build_args['path'] = deepcopy(options['build']['context'])
                        else:
                            print "Please provide with the build context path by mentioning 'context' under build tag"
                        if "dockerfile" in options["build"]:
                            build_args['dockerfile'] = deepcopy(options["build"]["dockerfile"])
                        if "args" in options["build"]:
                            build_args['dockerfile'] = deepcopy(options['build']["args"])
                        if "cache_form" in options['build']:
                            build_args['cache_from'] = deepcopy(options['build']['cache_from'])
                        else:
                            "Enter a correct parameter for service %s"%service
                    else:
                        build_args['path'] = deepcopy(options['build'])
                        build_args['dockerfile'] = deepcopy("Dockerfile")
                elif option == "image":
                    kwargs['image'] =  deepcopy(options['image'])
                elif option == "command":
                    kwargs['command'] = deepcopy(options['command'])
                # elif option == "args":
                #     pass
                # elif option == "constraints":
                #     pass
                elif option == "labels":
                    if type(options['labels']) == dict:
                        kwargs['container_labels'] = deepcopy(options['labels'])
                    else:
                        pass

                # elif option == "env":
                #     pass
                # elif option == "hostname":
                #     pass
                # elif option == "labels":
                #     pass
                # elif option == "log_driver":
                #     pass
                # elif option == "log_driver_options":
                #     pass
                # elif option == "container_name":
                #     pass
                # elif option == "credential_spec":
                #     pass
                elif option == "deploy":
                    serviceMode = {'mode':'replicated','replicas':1}
                    if "mode" in options['deploy']:
                        serviceMode['mode'] = options['deploy']['mode']
                    if "replicas" in options['deploy']:
                        serviceMode['mode'] = options['deploy']['replicas']
                    kwargs['mode'] = docker.types.ServiceMode(mode=serviceMode['mode'],replicas=serviceMode['replicas'])
                    if "placement" in options['deploy']:
                        kwargs['constraints'] = options['deploy']['placement']['constraints']
                    if "update_config" in options['deploy']:
                        configurationDict = self.getUpdateConfig(options['deploy']['update_config'])
                        kwargs['update_config'] = docker.types.UpdateConfig(parallelism = configurationDict['parallelism'], delay = configurationDict['delay'], failure_action = 'continue', monitor = configurationDict['monitor'], max_failure_ratio = configurationDict['max_failure_ratio'])
                    if "resources" in options['deploy']:
                        resourceDict = self.getResources(options['deploy']['resources'])
                        kwargs['resources'] = docker.types.Resources(cpu_limit=resourceDict['cpu_limit'], mem_limit=resourceDict['mem_limit'], cpu_reservation=resourceDict['cpu_reservation'], mem_reservation=resourceDict['mem_reservation'])
                    if "restart_policy" in options['deploy']:
                        policyDict = self.getRestartPolicy(options['deploy']['restart_policy'])
                        kwargs['restart_policy'] = docker.types.RestartPolicy(condition=policyDict['condition'], delay=policyDict['delay'], max_attempts=policyDict['max_attempts'], window=policyDict['window'])
                    # if "labels" in options['deploy']:
                    #     pass
                elif option == "depends_on":
                    depends_on = options['depends_on']
                # elif option == "entrypoint":
                #     pass
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
                        kwargs['env'] = envList
                    else:
                        kwargs['env'] = options['environment']

                # elif option == "expose":
                #     pass
                # elif option == "extra_hosts":
                #     pass
                # elif option == "healthcheck":
                #     pass
                elif option == "logging":
                    kwargs['log_driver']= options['logging']['driver']
                    kwargs['log_driver_options'] = options['logging']['options']
                elif option == "networks":
                    kwargs['networks'] = options['networks']
                elif option == "pid":
                    pass
                elif option == "ports":
                    ports = dict()
                    for port in options['ports']:
                        if '/' in port:
                            protocol = port.rsplit('/')[1]
                            port = port.rsplit('/')[0]
                            ports[port.rsplit(':',1)[1]] = (port.rsplit(':',1)[0],protocol)
                        elif ':' not in port:
                            ports[port] = port
                        else:
                            ports[port.rsplit(':', 1)[1]] = port.rsplit(':', 1)[0]
                    kwargs['endpoint_spec'] = docker.types.EndpointSpec(mode='vip', ports=ports)
                elif option == "volumes":
                    kwargs['mounts'] = options['volumes']
                elif option == "secrets":
                    kwargs['secrets'] = options['secrets']
                # elif option == "ulimits":
                #     pass
                elif option == "hostname":
                    kwargs['hostname'] = options['hostname']
                elif option == "user":
                    kwargs['user'] = options['user']
                elif option == "working_dir":
                    kwargs['workdir'] = options['working_dir']
                #elif option == ""
            print kwargs


    def deploy(self,dict):
        serviceMode = {'mode': 'replicated', 'replicas': 1}
        if "mode" in dict['deploy']:
            serviceMode['mode'] = dict['deploy']['mode']
        if "replicas" in dict['deploy']:
            serviceMode['mode'] = dict['deploy']['replicas']
        kwargs['mode'] = docker.types.ServiceMode(mode=serviceMode['mode'], replicas=serviceMode['replicas'])
        if "placement" in dict['deploy']:
            kwargs['constraints'] = dict['deploy']['placement']['constraints']
        if "update_config" in dict['deploy']:
            configurationDict = self.getUpdateConfig(dict['deploy']['update_config'])
            kwargs['update_config'] = docker.types.UpdateConfig(parallelism=configurationDict['parallelism'],
                                                                delay=configurationDict['delay'],
                                                                failure_action='continue',
                                                                monitor=configurationDict['monitor'],
                                                                max_failure_ratio=configurationDict[
                                                                    'max_failure_ratio'])
        if "resources" in dict['deploy']:
            resourceDict = self.getResources(dict['deploy']['resources'])
            dict['resources'] = docker.types.Resources(cpu_limit=resourceDict['cpu_limit'],
                                                         mem_limit=resourceDict['mem_limit'],
                                                         cpu_reservation=resourceDict['cpu_reservation'],
                                                         mem_reservation=resourceDict['mem_reservation'])
        if "restart_policy" in dict['deploy']:
            policyDict = self.getRestartPolicy(dict['deploy']['restart_policy'])
            kwargs['restart_policy'] = docker.types.RestartPolicy(condition=policyDict['condition'],
                                                                  delay=policyDict['delay'],
                                                                  max_attempts=policyDict['max_attempts'],
                                                                  window=policyDict['window'])

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

    def create_service(self):
        pass
service = Services()#'master','tcp://192.168.99.100:2376')
print service.getServicesList()