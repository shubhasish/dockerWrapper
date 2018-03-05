import requests
import config
import yaml
import sys

import logging

logging.basicConfig(format='%(levelname)s: %(message)s',stream=sys.stdout, level=logging.INFO)


class RequestHandler:
    def __init__(self,host="localhost",port=5001):
        self.host = host
        self.port = port

    def createRequestHandler(self,content):
        url = "http://%s:%s%s"%(self.host,self.port,config.API_DICT['create'])
        r = requests.post(url= url, json=content)
        logging.info(r.text)
        return r.status_code

    def swarmRequestHandler(self,swarmName):
        url = "http://%s:%s%s" % (self.host, self.port, config.API_DICT['swarm'])
        r = requests.post(url=url, json={'swarm':swarmName})
        logging.info(r.text)
        return r.status_code

    def portainerHandler(self):
        url = "http://%s:%s%s" % (self.host, self.port, config.API_DICT['manage'])
        r = requests.post(url=url)
        logging.info(r.text)
        return r.status_code

    def telegrafHandler(self,path,influxDb):
        url = "http://%s:%s%s" % (self.host, self.port, config.API_DICT['monitor'])
        file = {"telegraf":open(path,'rb+')}
        r = requests.post(url=url,data={'path':path,'influxDB':influxDb},files=file)
        logging.info(r.text)
        return r.status_code

    def deployHandler(self,path,service):
        self.yml = open(path, 'r+')
        fileName = {'deploymentFile':self.yml}
        data = {'serviceName':service}
        url = "http://%s:%s%s" % (self.host, self.port, config.API_DICT['deploy'])
        r = requests.post(url=url, data=data,files=fileName)
        logging.info(r.text)
        return r.status_code
        # print "Ok"