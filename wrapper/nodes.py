import docker
import subprocess


class Nodes(object):
    def __init__(self):
        pass

    def listNodes(self,client):
        try:
            return {"Error":False,"Message":client.nodes.list()}
        except Exception as e:
            return {"Error":True,"Message":e.message}
    def checkNodes(self):
        x=subprocess.Popen("docker-machine ls",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output,err=x.communicate()
        return output

    def createNode(self,node):
        name = node['name']
        driver = node['driver']
        role = node['role']
        subprocess.call(['docker-machine','create','-driver',driver,name])
# client = docker.from_env()
# nodeList = listNodes(client)
# if nodeList['Error']:
#     print "Hello"
# else:
#     print "World"