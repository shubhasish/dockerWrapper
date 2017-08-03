import docker
import pickledb
from config import DM_URL
from config import WRAPPER_DB_PATH
from modules.machine import Machine

from flask_restful import Resource
from flask import Response
from config import getClient

class RegistryHandler(Resource):
    def post(self):
        self.template()
        if self.SERVERS:
            registry = self.createRegistry()
            return {'registry':registry}
        else:
            return Response("Check if you have already initialized cluster", mimetype='text/xml')

    def template(self):
        self.SERVERS = dict()
        self.manager = Machine(path=DM_URL)
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH,False)
            self.SERVERS = self.db.get('servers')
        except Exception as e:
            pass

    def createRegistry(self):
        self.master = [x for x in self.SERVERS.keys() if self.SERVERS[x]['init']][0]
        self.masterMachine = getClient(self.master, self.SERVERS[self.master]['url'])
        kwargs = {"name": "registry","endpoint_spec": docker.types.EndpointSpec(mode='vip', ports={5000: 5000}),"constraints":["node.hostname==registry"]}
        registry_service = self.masterMachine.services.create(image ="registry:2",**kwargs)
        return registry_service.id
