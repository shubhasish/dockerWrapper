from tls import TLS
import docker
import yaml
from copy import deepcopy


class Services:
    image = ""
    command = ""
    args = ""
    constraints = ""
    container_labels = ""
    endpoint_spec = ""
    env = ""
    hostname = ""
    labels = ""
    log_driver = ""
    log_driver_options = ""
    mode = ""
    mounts = ""
    name = ""
    networks = ""
    resources = ""
    restart_policy = ""
    secrets = ""
    stop_grace_period = ""
    update_config = ""
    user = ""
    workdir = ""

    def __init__(self,name,url,deploymentFile='../composer/docker-compose.yml'):

################### Variables......
        self.build = ""
        self.context = ""
        self.dockerFile = ""
        self.buildArgs = dict()
########### Initialization
        tls = TLS()
        self.tlsConfig = tls.getTLSconfig(name)
        self.stream = open(deploymentFile, 'r')
        self.client = docker.DockerClient(base_url=url, tls=self.tlsConfig)

    def listServices(self):
        return self.client.services.list()

    def getServicesList(self):
        services =  yaml.load(self.stream)['services']
        kwargs = {}
        for service in services:
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
                        build_args['path'] = options['build']
                        build_args['dockerfile'] = "Dockerfile"
                elif option == "image":
                    kwargs['image'] =  options['image']
                elif option == "command":
                    kwargs['command'] = options['command']
                elif option == "args":
                    pass
                elif option == "constraints":
                    pass
                elif option == "container_label":
                    pass
                elif option == "endpoint_specs":
                    pass
                elif option == "env":
                    pass
                elif option == "hostname":
                    pass
                elif option == "labels":
                    pass
                elif option == "log_driver":
                    pass
                elif option == "log_driver_options":
                    pass
                elif option == "container_name":
                    pass
                elif option == "credential_spec":
                    pass
                elif option == "deploy":
                    if "mode" in option['deploy']:
                        pass
                    if "replicas" in option['deploy']:
                        pass
                    if "placement" in option['deploy']:
                        pass
                    if "update_config" in option['deploy']:
                        pass
                    if "resources" in option['deploy']:
                        pass
                    if "restart_policy" in option['deploy']:
                        pass
                    if "labels" in option['deploy']:
                        pass
                elif option == "depends_on":
                    pass
                elif option == "entrypoint":
                    pass
                elif option == "env_file":
                    pass
                elif option == "environment":
                    pass
                elif option == "expose":
                    pass
                elif option == "extra_hosts":
                    pass
                elif option == "healthcheck":
                    pass
                elif option == "logging":
                    pass
                elif option == "networks":
                    pass
                elif option == "pid":
                    pass
                elif option == "ports":
                    pass
                elif option == "volumes":
                    pass
                elif option == "secrets":
                    pass
                elif option == "ulimits":
                    pass
                elif option == "restart":
                    pass
                elif option == "driver":
                    pass
                elif option == "driver_opts":
                    pass
                #elif option == ""

    def create_service(self):
        pass
service = Services('master','tcp://192.168.99.100:2376')
print service.getServicesList()