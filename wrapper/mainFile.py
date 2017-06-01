from parser import Parser
import docker
import subprocess
from nodes import Nodes
from swarm import Swarm

nameUrlList = {}
nameRoleList = {}
managerSet= set()
slaveSet =set()
parser = Parser()
nodes = parser.getNode()
nodeClient = Nodes()
output = nodeClient.checkNodes()
swarm = Swarm()

total_nodes = output.split('\n')
for i in range(1,len(total_nodes)):
    detailsList = total_nodes[i].split()
    if len(detailsList)>1:
        nameUrlList[detailsList[0]]=detailsList[4]



for node in nodes:
    role = node['role']
    if role.lower() == 'manager':
        managerSet.add(node['name'])
    else:
        slaveSet.add(node['name'])
    if node['name'] in nameUrlList:
        print "Node already present so skipping creation"
        continue
    else:
        nodeClient.createNode(node)

init_node = managerSet.pop()
init_node_url = nameUrlList[init_node]
init = swarm.swarmInit(init_node_url)
print init
print slaveSet

