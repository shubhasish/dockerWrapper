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
                  "Command to deploy/redploy a single service or multiple services\n\n" \
                  "Option:\n" \
                  "help-: show usage details\n" \
                  "-p --path-: path to the docker-compose '.yml or .yaml' file"
        elif arguments[2] == "-p" or arguments[2] == "--path":
            if os.path.isfile(arguments[3]) and (".yaml" in arguments[3] or ".yml" in arguments[3]):
                deploy = Deployment(path=arguments[3])
            else:
                print "Not a valid file, provide a valid file path"
        os._exit(0)
    else:
        print "\nNo path to file is provided. \nProvide a valid file path. Use 'wrapper create --help' for more "
        os._exit(0)

    # try:
    #     MASTER = file.readFile('shape.memory')
    #     existingCluster = set(MASTER.keys())
    # except Exception as e:
    #     print e
    #     print "Cluster hasn't been initialized in this folder yet. Please initialize Cluster"
    #     os._exit(0)
    # master = [x for x in existingCluster if MASTER[x]['init']==True][0]
    # swarmMaster = Swarm(name=master, url=MASTER[master]['url'])
    # swarmMaster.deploy()
    # dockerMachine.copy_composeFile()
    # dockerMachine.remove_stack(master)
    # dockerMachine.deploy_stack(master)
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

elif arguments[1] == "creata":
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
        # print "\nNo path to file is provided. \nProvide a valid file path. Use 'wrapper create --help' for more "
        swarm = Swarm_Handler()
        swarm.checkNswarm()
        os._exit(0)

if arguments[1] == "create":
    ###### File Reading
    try:
        print "Starting the wrapper Application"
        configuration = file.readFile('config.json')
        requiredMachines = set(configuration.keys())
    except Exception as e:
        print e
        os._exit(1)
    try:
        MASTER = file.readFile('shape.memory')
        existingCluster = set(MASTER.keys())
    except Exception as e:
        print e

    ######

    if len(existingCluster) == 0:
        print "No nodes are present in this cluster"
        createList = requiredMachines
        createMachines(createList,configuration)
        swarmList = createList
    else:
        print "Following nodes are present in the cluster"
        for node in existingCluster:
            print "%s \t %s" % (node, configuration[node]['role'])
        createList = requiredMachines.difference(existingCluster)
        createMachines(createList,configuration)
        swarmList = set([x for x in existingCluster if MASTER[x]['swarm'] == False])
        masterNode = [x for x in existingCluster if MASTER[x]['init'] == True]
        ##### Swarm Initialization

        if len(masterNode) > 0:
            print "Swarm has been initialized"

            print "Obtaining join token for %s" % masterNode[0]
            output = dockerMachine.checkSwarm(masterNode[0])
            managerToken = [x for x in output[1] if 'SWMTKN' in x][0]
            workerToken = [x for x in output[2] if 'SWMTKN' in x][0]
            swarmIp = MASTER[masterNode[0]]['ip']
            swarm_init = True
        else:
            print "Swarm hasn't been initialized"
            swarm_init = False

    ###### SWARM addition
    swarmList = createList.union(swarmList)
    if swarm_init:
        print "Swarm already initialized"
        print "Adding new nodes to swarm cluster"
        for nodes in swarmList:
            swarm = Swarm(nodes, MASTER[nodes]['url'])
            if configuration[nodes]['role'].lower() == "manager":

                swarm.joinSwarm(ip=swarmIp, token=managerToken, listen=MASTER[nodes]['ip'])
            else:
                swarm.joinSwarm(ip=swarmIp, token=workerToken, listen=MASTER[nodes]['ip'])
    else:
        print "Initializing Swarm..."
        master = [x for x in swarmList if MASTER[x]['role'].lower() == "manager"][0]
        swarmMaster = Swarm(name=master, url=MASTER[master]['url'])
        swarmMaster.swarmInit(MASTER[master]['ip'])
        MASTER[master]['swarm'] = True
        MASTER[master]['init'] = True
        swarmMaster.create_network('icarus', 'overlay')
        dockerMachine.deploy_portainer(master)
        dockerMachine.deploy_registry(master)
        masterDetails = dockerMachine.checkSwarm(master)
        managerToken = [x for x in masterDetails[1] if 'SWMTKN' in x][0]
        workerToken = [x for x in masterDetails[2] if 'SWMTKN' in x][0]
        swarmList.remove(master)
        for nodes in swarmList:
            swarm = Swarm(nodes, MASTER[nodes]['url'])
            if configuration[nodes]['role'].lower() == "manager":

                swarm.joinSwarm(ip=MASTER[master]['ip'], token=managerToken, listen=MASTER[nodes]['ip'])
                MASTER[nodes]['swarm'] = True
            else:
                swarm.joinSwarm(ip=MASTER[master]['ip'], token=workerToken, listen=MASTER[nodes]['ip'])
                MASTER[nodes]['swarm'] = True
    # master = "master"
    # url = "tcp://192.168.99.101:2376"
    # swarmMaster = Swarm(name=master, url=url)

        swarmMaster.buildImage()
        dockerMachine.copy_composeFile()

        dockerMachine.deploy_stack(master)
        if len(MASTER.keys()) > 0:
            file.writeFile(MASTER)

if arguments[1] == "redeploy":
    try:
        MASTER = file.readFile('shape.memory')
        existingCluster = set(MASTER.keys())
    except Exception as e:
        print e
        print "Cluster hasn't been initialized in this folder yet. Please initialize Cluster"
        os._exit(0)
    master = [x for x in existingCluster if MASTER[x]['init']==True][0]
    swarmMaster = Swarm(name=master, url=MASTER[master]['url'])
    swarmMaster.deploy()
    dockerMachine.copy_composeFile()
    dockerMachine.remove_stack(master)
    dockerMachine.deploy_stack(master)
    os._exit(0)