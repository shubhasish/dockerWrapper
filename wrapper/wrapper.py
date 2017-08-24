import json
import os
import copy
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config import CONFIG_FORMATT, API_DICT, WRAPPER_DB_PATH

from content import MAIN_HELP
from content import DEPLOY_HELP
from content import WRAPUP_HELP
from content import CREATE_HELP
from content import SWARMIT_HELP
from content import REDEPLOY_HELP
from content import PATH_ERROR


from modules.dockerMachine import dockerMachine
from modules.fileFormatter import File
from modules.swarm import Swarm
from API_connector import RequestHandler

from components.removal_manager import RemovalManager
from components.server_setup import Server
from components.swarm_handler import Swarm_Handler
from components.deployment_handler import Deployment
from components.agent import Agent
import sys
import pickledb

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

helpSet = set(['--h','--help','help','-h'])


def fileChecker(path,extention):
    if os.path.isfile(path):
        if any(x in path for x in extention):
            return True
        else:
            return False
    else:
        return False
##### Handler Classes
fileReader = File()



##### Command Line Handler
number_of_argument = len(sys.argv)
arguments = sys.argv

##### Help Module
if any(arguments[1].lower()==x for x in helpSet):
    print MAIN_HELP

##### Create Module
elif arguments[1] == "create":
    options = arguments[2:]

    for index,option in enumerate(options):
        if any(x in options for x in helpSet):
            print CREATE_HELP
            os._exit(0)
        elif any(option == x for x in ['-p','--path']):
            try:
                file = options[index+1]
                if fileChecker(file,('json')):
                    try:
                        print "Reading Configuration File"
                        file = fileReader.readFile(file)
                        create_req = RequestHandler()
                        create_req.createRequestHandler(file)

                    except Exception as e:
                        print e
                        print "Exiting Cluster Creation Process"
                        os._exit(1)
                    # setup = Server()
                    # setup.create_cluster(file)
                else:
                    print PATH_ERROR
                    os._exit(1)
            except Exception as e:
                print e
                print PATH_ERROR
                os._exit(1)
        else:
            print "Enter a valid create options, Use 'wrapper create --help' for more info."
            os._exit(0)

##### Swarm Module
elif arguments[1].lower() == "swarmit":
    options = arguments[2:]
    if any(x in options for x in helpSet):
        print SWARMIT_HELP
    elif len(options) == 1 and options[0].isalnum():
        create_req = RequestHandler()
        create_req.swarmRequestHandler(options[0])
    else:
        print "Not a valid swarm function, use 'wrapper swarmit --help' for more details."

##### Deploy Module
elif arguments[1] == "deploy":
    options = arguments[2:]
    if any(x in options for x in helpSet):
        print DEPLOY_HELP
        os._exit(0)
    path = None
    for index,option in enumerate(options):
        if any(option == x for x in ['-p','--path']):
            try:
                file = options[index+1]

                if fileChecker(options[index+1],('yaml','yml')):
                    path = options[index+1]

                    # deploy = Deployment()
                    # deploy = deploy.deployService(path=options[index+1],option=deployOption)
                else:
                    print PATH_ERROR
                    os._exit(1)
            except Exception as e:
                print e
                print PATH_ERROR
                os._exit(1)
        else:
            continue
            print "Enter a valid deployment options, Use 'wrapper deploy --help' for more info"
    deployOption = options[len(options) - 1]
    create_req = RequestHandler()
    create_req.deployHandler(path=path, deployOption=deployOption)

######## Redeploy module
elif arguments[1] == "redeploy":
    if number_of_argument > 2:
        if any(arguments[2].lower()==x for x in helpSet):
            print REDEPLOY_HELP
        elif arguments[2] == "-p" or arguments[2] == "--path":
            if os.path.isfile(arguments[3]) and (".yaml" in arguments[3] or ".yml" in arguments[3]):
                try:
                    deploy = Deployment()
                    deploy.reDeploy(path=arguments[3],serviceName=arguments[4])
                except Exception as e:
                    print e
            else:
                print "Not a valid file, provide a valid file path"
        os._exit(0)
    else:
        print "\nNo path to file is provided. \nProvide a valid file path. Use 'wrapper create --help' for more "
        os._exit(0)

###### Wrap Up Module
elif arguments[1].lower() == "wrapup":
    rm = RemovalManager()
    options = arguments[2:]
    if any(x in options for x in helpSet):
        print WRAPUP_HELP
        os._exit(0)
    if len(options)==0:
        print "\nPlease enter a valid cleanup options, Use 'wrapper wrapUp help' for more info"
        os._exit(0)
    print rm.removeNodes(options)

###### Agnet Module
elif arguments[1] == "agent":
    if arguments[2] == "start":
        options = arguments[3:]
        if len(options)==0:
            print "Please provide configuration"
            os._exit(0)
        host = None
        port = None

        for i,option in enumerate(options):
            if option == "--host":
                host = options[i+1]
            elif option == "--port":
                port = options[i+1]
        db = pickledb.load(WRAPPER_DB_PATH, False)
        db.set('host',host)
        db.set('port',port)
        db.dump()

        agent = Agent(host=host,port=int(port))
        agent.startAgent()
    if arguments[2] == "stop":
        db = pickledb.load(WRAPPER_DB_PATH,False)
        host = db.get('host')
        port = db.get('port')

        url = 'http://%s:%s'%(host,port)+\
              API_DICT['shutdown']
        requests.post(url)

else:
    print MAIN_HELP
