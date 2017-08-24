import requests
import config
import yaml

class RequestHandler:
    def __init__(self,host="localhost",port=5000):
        self.host = host
        self.port = port

    def createRequestHandler(self,content):
        url = "http://%s:%s%s"%(self.host,self.port,config.API_DICT['create'])
        r = requests.post(url= url, json=content)
        return r.status_code

    def swarmRequestHandler(self,swarmName):
        url = "http://%s:%s%s" % (self.host, self.port, config.API_DICT['swarm'])
        r = requests.post(url=url, json={'swarm':swarmName})
        return r.status_code

    def deployHandler(self,path,deployOption):
        self.yml = open(path, 'r+')
        fileName = {'deploymentFile':self.yml}
        data = {'serviceName':deployOption}
        url = "http://%s:%s%s" % (self.host, self.port, config.API_DICT['deploy'])
        r = requests.post(url=url, data=data,files=fileName)
        return r.status_code
        # print "Ok"