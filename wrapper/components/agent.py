from flask import Flask
from flask_restful import Api
from flask import request
from flask_restful import Resource

from config import API_DICT

from monitoring import Monitoring
from server_setup import Server
from swarm_handler import Swarm_Handler
from deployment_handler import Deployment
from service_handler import  ListServices,GetService, ListTasks, RemoveService
from nodes_handler import GetNodes, ListNodes, UpdateNodes
from manage import Manager
from monitoring import Monitoring
from autoSacling import Horizontal



class Agent(Resource):
    def __init__(self,host='0.0.0.0',port=5000):
        self.host = host
        self.port = port


    def post(self):
        self.shutdown_server()
        return 'Server shutting down...'

    def get(self):
        return 'Wrong Method, Use POST instead'

    def startAgent(self):
        app = Flask(__name__)


        api = Api(app)
        api.add_resource(Agent,API_DICT['shutdown'])
        api.add_resource(Server,API_DICT['create'])
        api.add_resource(Swarm_Handler,API_DICT['swarm'])
        api.add_resource(GetService, API_DICT['service_get'])
        api.add_resource(ListServices, API_DICT['service_list'])
        api.add_resource(RemoveService, API_DICT['service_remove'])
        api.add_resource(ListTasks, API_DICT['service_task'])
        api.add_resource(GetNodes, API_DICT['node_get'])
        api.add_resource(ListNodes, API_DICT['node_list'])
        api.add_resource(UpdateNodes, API_DICT['node_update'])
        api.add_resource(Deployment, API_DICT['deploy'])
        api.add_resource(Manager, API_DICT['manage'])
        api.add_resource(Monitoring, API_DICT['monitor'])
        api.add_resource(Horizontal,API_DICT['hori_scale'])




        app.run(debug=True, host=self.host,port=self.port,use_reloader=False)


    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()