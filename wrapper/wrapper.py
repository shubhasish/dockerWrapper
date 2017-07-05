import json
import os
import copy
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config import CONFIG_FORMATT
from modules.dockerMachine import dockerMachine
from modules.fileFormatter import File
from modules.swarm import Swarm

from components.removal_manager import RemovalManager
from components.server_setup import Server
from components.swarm_handler import Swarm_Handler
from components.deployment_handler import Deployment
import sys

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


MASTER = {}
requiredMachines = createList = existingCluster = memory = configuration = swarm_init = managerToken = workerToken = masterNode = swarmIp = ''
file = File()
dockerMachine = dockerMachine()


def createMachines(createList,configuration):
    print configuration
    if len(createList) > 0:
        print "Following nodes will be created"
        master = []
        print
        for node in createList:
            print configuration[node]
            print "%s \t %s" % (node, configuration[node]['role'])
        for node in createList:
            print "Creating the node %s" % node
            dockerMachine.createMachine(name=node, driver=configuration[node]['driver'],configurations=configuration[node])
            config = CONFIG_FORMATT
            config['url'] = dockerMachine.getURL(node)
            config['ip'] = dockerMachine.getIp(node)
            config['role'] = configuration[node]['role']
            config['driver'] = configuration[node]['driver']
            MASTER[node] =copy.deepcopy(config)


    else:
        print "No new machines to be created"

number_of_argument = len(sys.argv)
arguments = sys.argv

if arguments[1] == "deploy":
    if number_of_argument > 2:
        if arguments[2] == "help" or arguments[2] == "--help":
            print "\nUsage: wrapper deploy [OPTIONS] <service-name>/all \n\n" \
                  "Command to deploy a single service or multiple services\n\n" \
                  "Option:\n" \
                  "help-: show usage details\n" \
                  "-p --path-: path to the docker-compose '.yml or .yaml' file"
        elif arguments[2] == "-p" or arguments[2] == "--path":
            if os.path.isfile(arguments[3]) and (".yaml" in arguments[3] or ".yml" in arguments[3]):
                try:
                    arguments[4]
                    deploy = Deployment(path=arguments[3])
                    deploy.deployService(option=arguments[4])
                except Exception as e:
                    print "No options provided, so deploying all services."
                    deploy = Deployment(path=arguments[3])
                    deploy.deployService(option='all')

            else:
                print "Not a valid file, provide a valid file path"
        os._exit(0)
    else:
        print "\nNo path to file is provided. \nProvide a valid file path. Use 'wrapper create --help' for more "
        os._exit(0)

    os._exit(0)

elif arguments[1].lower() == "wrapup":
    rm = RemovalManager()
    if number_of_argument > 2:
        if arguments[2] == "help" or arguments[2] == "--help":
            print "\nUsage: wrapper wrapUp [OPTIONS] \n\n" \
                  "Command to remove single node or multiple nodes from cluster\n\n" \
                  "Option:\n" \
                  "help-: show usage details\n" \
                  "all-: remove all nodes from cluster\n" \
                  "node/nodes[NAME]-: nodes name comma separated\n"

        else:
            rm.removeNodes(arguments[2:])
        os._exit(0)
    else:
        print "\nPlease enter a valid option\nSee usage or type 'wrapper wrapUp help' for more details"
        os._exit(0)

elif arguments[1] == "create":
    if number_of_argument > 2:
        if arguments[2] == "help" or arguments[2] == "--help":
            print "\nUsage: wrapper create [OPTIONS] \n\n" \
                  "Command to create cluster\n\n" \
                  "Option:\n" \
                  "help: show usage details\n" \
                  "-p --path: path to config file\n"

        elif arguments[2]=="-p" or arguments[2]=="--path":
            if os.path.isfile(arguments[3]) and ".json" in arguments[3]:
                setup = Server(path=arguments[3])
                setup.create_cluster()
            else:
                print "Not a valid file, provide a valid file path"
        os._exit(0)
    else:
        print "\nNo path to file is provided. \nProvide a valid file path. Use 'wrapper create --help' for more "
        os._exit(0)


elif arguments[1].lower() == "swarmit":
    if number_of_argument > 2:
        if arguments[2] == "help" or arguments[2] == "--help":
            print "\nUsage: wrapper swarmit [OPTIONS] \n\n" \
                  "Command to create cluster\n\n" \
                  "Option:\n" \
                  "help: show usage details\n"

    else:
        swarm = Swarm_Handler()
        swarm.checkNswarm()
        os._exit(0)


if arguments[1] == "redeploy":
    if number_of_argument > 2:
        if arguments[2] == "help" or arguments[2] == "--help":
            print "\nUsage: wrapper redeploy [OPTIONS] <service-name>/everything \n\n" \
                  "Command to redploy a single service or multiple services\n\n" \
                  "Option:\n" \
                  "help-: show usage details\n" \
                  "-p --path-: path to the docker-compose '.yml or .yaml' file"
        elif arguments[2] == "-p" or arguments[2] == "--path":
            if os.path.isfile(arguments[3]) and (".yaml" in arguments[3] or ".yml" in arguments[3]):
                try:
                    deploy = Deployment(path=arguments[3])
                    deploy.reDeploy(serviceName=arguments[4])
                except Exception as e:
                    print e

            else:
                print "Not a valid file, provide a valid file path"
        os._exit(0)
    else:
        print "\nNo path to file is provided. \nProvide a valid file path. Use 'wrapper create --help' for more "
        os._exit(0)

