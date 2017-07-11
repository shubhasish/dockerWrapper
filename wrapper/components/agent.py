from flask import Flask
from flask_restful import Api
from flask import request
from flask_restful import Resource

from config import API_DICT

from deployment_handler import Deployment
from monitoring import Monitoring
from server_setup import Server
from swarm_handler import Swarm_Handler
from removal_manager import RemovalManager


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

        # app.config['DEBUG'] = True

        api = Api(app)
        api.add_resource(Agent,API_DICT['shutdown'])
        api.add_resource(Server,API_DICT['create'])
        api.add_resource(Swarm_Handler,API_DICT['swarm'])
        api.add_resource(RemovalManager,API_DICT['wrapup'])

        # @app.route(API_DICT['create'],methods=['POST'])
        # def printI():
        #     print request.get_json()
        #     return "Hello"


        app.run(debug=True, host=self.host,port=self.port)


    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()