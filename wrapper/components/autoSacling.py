from flask_restful import Resource
import pickledb
from config import DM_URL, WRAPPER_DB_PATH
from config import getClient, dir_path
import re
from docker import APIClient, types
from flask import request
from modules.tls import TLS
from service_handler import GetService


class Horizontal(Resource):
    def template(self):
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH, False)
            self.SERVERS = self.db.get('servers')
            self.swarm = self.db.get('swarm')
        except Exception as e:
            pass

    def getMasterMachine(self):
        self.master = [x for x in self.SERVERS.keys() if self.SERVERS[x]['init']][0]
        tls = TLS()
        tlsConfig = tls.getTLSconfig(self.master)
        self.cli = APIClient(base_url=self.SERVERS[self.master]['url'], tls=tlsConfig)

    def post(self):
        json = request.get_json()
        level = json['level']
        message = json['message']
        regex = re.compile('Service:(.+?)\s')
        service = regex.findall(message)[0]
        self.template()
        self.getMasterMachine()
        if level == "OK":
            return "OK"
        elif level == "INFO":
            return self.autoScale({"service":service,"scale":"down"})
        elif level == "WARNING":
            return "Warn"
        else:
            return self.autoScale({"service": service, "scale": "up"})


    def autoScale(self,json):
        servicename = json['service']
        scale = json['scale']
        service = self.cli.inspect_service(servicename)
        version = service['Version']["Index"]
        task_template = service["Spec"]["TaskTemplate"]

        networks = service["Spec"]["Networks"]
        replicas = service["Spec"]["Mode"]["Replicated"]["Replicas"]
        new_replicas = 0

        if scale == "up":

            new_replicas = replicas + 1
            print new_replicas
        elif scale == "down":
            if replicas == 1:
                return "Success"
            else:
                new_replicas = replicas - 1

        serviceMode = types.ServiceMode(mode='replicated', replicas=new_replicas)
        try:
            print self.cli.update_service(servicename,version,mode=serviceMode,task_template=task_template,networks=networks,name=servicename)
            return "Success"
        except Exception as e:
            print e
            return "Failure"
