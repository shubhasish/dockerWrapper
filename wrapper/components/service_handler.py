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

def serviceFormater(service):
    return {'id':service.id,'short_id':service.short_id,'attrs':service.attrs,'version':service.version,'name':service.name}

class ListServices(Resource):

    def post(self):
        return 'Wrong Mehotd, Use GET instead'


    def get(self):
        services = self.listServices()
        return services

    def listServices(self):
        servers = getServers()
        if servers:
            masterList = getMaster()
            if masterList:
                url = servers[masterList[0]]['url']
                name = masterList[0]
                client = getClient(name,url)
                services = client.services.list()

                return {'status':'success','message':[serviceFormater(x) for x in services]}
            else:
                return {'status':'failure','message':'Swarm has not been initialized. Please initialize swarm'}
        else:
            return {'status':'failure','message':'No servers found registered with this Agent. Please Initialize nodes using \'wrapper create\''}

class GetService(Resource):
    def post(self):
        return 'Wrong Method, Use GET instead'

    def get(self,name):
        service = self.getService(name)

        return service

    def getService(self,serviceName):
        servers = getServers()
        if servers:
            masterList = getMaster()
            if masterList:
                url = servers[masterList[0]]['url']
                name = masterList[0]
                client = getClient(name, url)
                services = client.services.list()
                service = [serviceFormater(x) for x in services if x.name == serviceName]
                if service:
                    return {'status': 'success', 'message': service[0]}
                else:
                    return {'status': 'failure', 'message': 'No such service found, Enter a valid service name'}
            else:
                return {'status': 'failure', 'message': 'Swarm has not been initialized. Please initialize swarm'}
        else:
            return {'status': 'failure',
                    'message': 'No servers found registered with this Agent. Please Initialize nodes using \'wrapper create\''}

class RemoveService(Resource):
    def get(self):
        return 'Wrong Method, Use DELETE instead'
    def post(self):
        return 'Wrong Method, Use DELETE instead'
    def delete(self):
        serviceName = request.form['serviceName']
        status = self.deleteService(serviceName)
        return status

    def deleteService(self,serviceName):
        servers = getServers()
        if servers:
            masterList = getMaster()
            if masterList:
                url = servers[masterList[0]]['url']
                name = masterList[0]
                client = getClient(name, url)
                services = client.services.list()
                if serviceName == 'all':
                    for service in services:
                        try:
                            if service.name == 'regitry':
                                continue
                            else:
                                service.remove()

                        except Exception as e:
                            return {'status': 'failure', 'message': e.message}
                    return {'status': 'success', 'message': 'Services removed successfully'}
                else:
                    service = [x for x in services if x.name == serviceName]
                    if service:
                        try:
                            service[0].remove()
                            return {'status': 'success', 'message': 'Service removed successfully'}
                        except Exception as e:
                            return {'status':'failure','message':e.message}
                    else:
                        return {'status': 'success', 'message': 'No such service found, Enter a valid service name'}
            else:
                return {'status': 'failure', 'message': 'Swarm has not been initialized. Please initialize swarm'}
        else:
            return {'status': 'failure',
                    'message': 'No servers found registered with this Agent. Please Initialize nodes using \'wrapper create\''}


class ListTasks(Resource):
    def post(self):
        return 'Wrong Method, Use GET intead'

    def get(self,name):
        task = self.getTasks(name)
        return task

    def getTasks(self,serviceName):
        servers = getServers()
        if servers:
            masterList = getMaster()
            if masterList:
                url = servers[masterList[0]]['url']
                name = masterList[0]
                client = getClient(name, url)
                services = client.services.list()
                tasks =[x.tasks() for x in services if x.name == serviceName]
                if tasks:
                    return {'status': 'success', 'message': tasks}
                else:
                    return {'status':'failure', 'message':'No such service found, Enter a valid service name'}
            else:
                return {'status': 'failure', 'message': 'Swarm has not been initialized. Please initialize swarm'}
        else:
            return {'status': 'failure',
                    'message': 'No servers found registered with this Agent. Please Initialize nodes using \'wrapper create\''}

