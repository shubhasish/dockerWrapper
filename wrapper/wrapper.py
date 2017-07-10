import json
import os
import copy
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config import CONFIG_FORMATT

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

from components.removal_manager import RemovalManager
from components.server_setup import Server
from components.swarm_handler import Swarm_Handler
from components.deployment_handler import Deployment
import sys

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




##### Command Line Handler
number_of_argument = len(sys.argv)
arguments = sys.argv

if arguments[1] == "deploy":
    options = arguments[2:]
    for index,option in enumerate(options):
        if any(x in options for x in helpSet):
            print DEPLOY_HELP
            os._exit(0)
        elif any(option == x for x in ['-p','--path']):
            try:
                file = options[index+1]
                if fileChecker(options[index+1],('yaml','yml')):
                    deployOption = options[len(options) - 1]
                    deploy = Deployment()
                    deploy = deploy.deployService(path=option[index+1],option=deployOption)
                else:
                    print PATH_ERROR
                    os._exit(1)
            except Exception as e:
                print e
                print PATH_ERROR
                os._exit(1)
        else:
            print "Enter a valid deployment options, Use 'wrapper deploy --help' for more info"

elif arguments[1].lower() == "wrapup":
    rm = RemovalManager()
    options = arguments[2:]
    if any(x in options for x in helpSet):
        print WRAPUP_HELP
        os._exit(0)
    if len(options)==0:
        print "\nPlease enter a valid cleanup options, Use 'wrapper wrapUp help' for more info"
        os._exit(0)
    rm.removeNodes(options[2:])

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
                    setup = Server(path=arguments[3])
                    setup.create_cluster()
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


elif arguments[1].lower() == "swarmit":
    options = arguments[2:]

    if any(x in options for x in helpSet):
        print SWARMIT_HELP
    elif len(options) == 0:
        swarm = Swarm_Handler()
        swarm.checkNswarm()
    else:
        print "Not a valid swarm function, use 'wrapper swarmit --help' for more details."
elif any(arguments[1].lower()==x for x in helpSet):
    print MAIN_HELP

elif arguments[1] == "redeploy":
    if number_of_argument > 2:
        if any(arguments[2].lower()==x for x in helpSet):
            print REDEPLOY_HELP
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

elif arguments[1] == "agent":
    if arguments[2] == "start":
        from flask import Flask
        from flask_restful import Api

        from flask import request


        def shutdown_server():
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()

        app = Flask(__name__)
        app.config['DEBUG'] = True
        api = Api(app)


        @app.route('/shutdown', methods=['POST'])
        def shutdown():
            shutdown_server()
            return 'Server shutting down...'
        app.run(debug=True,host="127.0.0.1")
    if arguments[2] == "stop":
        import requests
        requests.post('http://127.0.0.1:5000/shutdown')


