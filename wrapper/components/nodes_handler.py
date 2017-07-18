from flask_restful import Resource, request
from config import WRAPPER_DB_PATH
from config import getClient
import pickledb

def getMaster():
    try:
        db = pickledb.load(WRAPPER_DB_PATH,False)
        masterNode = db.get('Master')
        return masterNode
    except Exception as e:
        print e
    return  None

def getServers():
    try:
        db = pickledb.load(WRAPPER_DB_PATH,False)
        servers = db.get('servers')
        return servers
    except Exception as e:
        print e
    return None

class ListNodes(Resource):

    def post(self):
        return "Wrong Mehotd, Use GET instead"


    def get(self):
        nodes = self.listNode()
        return nodes

    def listNode(self):
        servers = getServers()
        if servers:
            masterList = getMaster()[0]
            if masterList:
                url = servers[masterList[0]]['url']
                name = masterList[0]
                client = getClient(name,url)
                nodes = client.nodes.list()
                return {'status':'success','message':nodes}
            else:
                return {'status':'failure','message':'Swarm has not been initialized. Please initialize swarm'}
        else:
            return {'status':'failure','message':'No servers found registered with this Agent. Please Initialize nodes using \'wrapper create\''}


class GetNodes(Resource):

    def post(self):
        details = request.get_json()
        node = details['node']
        nodeDetails = self.getNode(node)
        return nodeDetails

    def get(self):
        return 'Wrong Method, Use POST instead'

    def getNode(self,node):
        servers = getServers()
        if servers:
            masterList = getMaster()[0]
            if masterList:
                url = servers[masterList[0]]['url']
                name = masterList[0]
                client = getClient(name, url)
                details = client.nodes.get(node)
                return {'status': 'success', 'message': details}
            else:
                return {'status': 'failure', 'message': 'Swarm has not been initialized. Please initialize swarm'}
        else:
            return {'status': 'failure',
                    'message': 'No servers found registered with this Agent. Please Initialize nodes using \'wrapper create\''}


class UpdateNodes(Resource):

    def post(self):
        details = request.get_json()
        node = details['node']
        specifications= details['node']
        updateStatus = self.updateNode(node,specifications)
        return updateStatus


    def get(self):
        return "Wrong Method, Use POST instead"

    def updateNode(self,node,specification):
        node = GetNodes.getNode(node)
        if node['status'] == "failure":
            return node
        try:
            node['message'].update(specification)
            return {'status':'success','message':'Node Updated Successfully'}
        except Exception as e:
            return {'status':'failure','message':e}
