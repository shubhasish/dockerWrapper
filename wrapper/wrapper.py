import os
import sys
import click
import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config import CONFIG_FORMATT, API_DICT, WRAPPER_DB_PATH

logging.basicConfig(format='%(levelname)s: %(message)s',stream=sys.stdout, level=logging.INFO)

from modules.fileFormatter import File
from API_connector import RequestHandler

from components.removal_manager import RemovalManager
from components.server_setup import Server
from components.swarm_handler import Swarm_Handler
from components.agent import Agent
import pickledb

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)




def getAgentConfig():
    db = pickledb.load(WRAPPER_DB_PATH, False)
    return (db.get('host'),db.get('port'))

def fileChecker(path):
    if os.path.isfile(path):
        return True
    else:
        return False


@click.group()
def cli():
    pass
##### Handler Classes

fileReader = File()

@cli.command()
@click.option('-p','--path',help="Path of the server configuration file")
@click.option('--agenthost',help="Host of the Wrapper Agent")
@click.option('--agentport',help="Port of the Wrapper Agent")
def create(path,agenthost,agentport):
    """Command to create docker nodes"""
    absolute_path = os.path.abspath(path)
    if agenthost and agentport:
        logging.info("Using the Host and Port passed through CLI for wrapper agent")
        req_handler = RequestHandler(agenthost,agentport)
        file = fileReader.readFile(absolute_path)
        req_handler.createRequestHandler(file)
    else:
        if fileChecker(absolute_path):
            try:
                logging.info("Reading Configuration File")
                logging.info("Creating docker-swarm nodes")
                server = Server()
                file = fileReader.readFile(absolute_path)
                server.create_cluster(file)

            except Exception as e:
                logging.error(e.message)
                logging.error("Exiting Cluster Creation Process")
                os._exit(1)

        else:
            logging.error("No such file found")


@cli.command()
@click.option('--clustername',help="Name of the swarm cluster")
@click.option('--agenthost',help="Host of the Wrapper Agent")
@click.option('--agentport',help="Port of the Wrapper Agent")
def swarmit(agenthost,agentport,clustername):
    """Command to add or remove the nodes from docker swarm"""
    if agenthost and agentport:
        logging.info("Using the Host and Port passed through CLI for wrapper agent")
        swrm_handler = RequestHandler(agenthost,agentport)
        swrm_handler.swarmRequestHandler(clustername)
    else:
        swarm = Swarm_Handler()
        result = swarm.checkNswarm(clustername)


@cli.command()
@click.option('--service',help="Name of the service")
@click.option('--all',is_flag=True,default=False,help="Deploy all services")
@click.option('--agenthost',help="Host of the Wrapper Agent")
@click.option('--agentport',help="Port of the Wrapper Agent")
@click.option('--path',help="Path of deployment yaml file")
def deployService(service,all,agenthost,agentport,path):
    """Command to deploy/update a service into swarm cluster the swarm cluster"""
    absolute_path = os.path.abspath(path)
    if fileChecker(absolute_path):
        logging.info("Valid File path")
    else:
        logging.error("invalid file path")
        os._exit(1)
    serviceName= None
    if all:
        serviceName = "all"
    else:
        serviceName = service
    if agenthost and agentport:
        logging.info("Using the Host and Port passed through CLI for wrapper agent")
        deployment_req = RequestHandler(agenthost,agentport)
        deployment_req.deployHandler(absolute_path,serviceName)
    else:
        db = pickledb.load(WRAPPER_DB_PATH, False)
        host = db.get('host')
        port = db.get('port')
        if host and port:
            deployment_req = RequestHandler(host,port)
            deployment_req.deployHandler(absolute_path,serviceName)
        else:
            logging.error("Start your wrapper agent first")


    os._exit(0)

@cli.command()
@click.option('--node',help="Name of the node")
@click.option("--all",is_flag=True,default=False,help="Remove all nodes")
def wrapup(node,all):
    """Command to wrapup the swarm cluster created"""
    rm = RemovalManager()
    if all:
        rm.removeNodes('all')
    elif node:
        rm.removeNodes(node)
    else:
        logging.error("Enter a valid node name")
    os._exit(0)


@cli.command()
@click.option('--agenthost',help="Host of the Wrapper Agent")
@click.option('--agentport',help="Port of the Wrapper Agent")
def deployPortainer(agenthost,agentport):
    """Command to deploy Portainer"""
    if agenthost and agentport:
        logging.info("Using the Host and Port passed through CLI for wrapper agent")
        portainer_req = RequestHandler(agenthost,agentport)
        portainer_req.portainerHandler()
    else:
        db = pickledb.load(WRAPPER_DB_PATH, False)
        host = db.get('host')
        port = db.get('port')
        if host and port:
            portainer_req = RequestHandler(host, port)
            portainer_req.portainerHandler()
        else:
            logging.error("Start your wrapper agent first")


@cli.command()
@click.option('--agenthost',help="Host of the Wrapper Agent")
@click.option('--agentport',help="Port of the Wrapper Agent")
@click.option('--path',help="Path of telegraf.txt")
@click.option('--influxdb',default='loclhost',help="InfluxDB host")
def deployTelegraf(agenthost,agentport,path,influxdb):
    """Command to start telegraf agent to collect metrices"""
    absolute_path = os.path.abspath(path)
    if fileChecker(absolute_path):
        logging.info("Valid File path")
    else:
        logging.error("invalid file path")
        os._exit(1)

    if agenthost and agentport:
        logging.info("Using the Host and Port passed through CLI for wrapper agent")
        telegraf_req = RequestHandler(agenthost,agentport)
        telegraf_req.telegrafHandler(absolute_path,influxdb)
    else:
        db = pickledb.load(WRAPPER_DB_PATH, False)
        host = db.get('host')
        port = db.get('port')
        if host and port:
            telegraf_req = RequestHandler(host,port)
            telegraf_req.telegrafHandler(absolute_path,influxdb)
        else:
            logging.error("Start your wrapper agent first")


@cli.command()
@click.option('--host',default="0.0.0.0",help="Host at which to start the Wrapper agent")
@click.option('--port',default='5000',help="Port at which to start the Wrapper agent")
def startAgent(host,port):
    """Command to start the Wrapper agent"""
    db = pickledb.load(WRAPPER_DB_PATH, False)
    db.set('host',host)
    db.set('port',port)
    db.dump()
    agent = Agent(host=host,port=int(port))
    agent.startAgent()


@cli.command()
def stopAgent():
    """Command to stop the Wrapper agent"""
    logging.info("Shutting down the local server.")
    db = pickledb.load(WRAPPER_DB_PATH, False)
    host = db.get('host')
    port = db.get('port')
    url = 'http://%s:%s' % (host, port)+"/v2/api/wrapper/shutdown"
    requests.post(url)
    db.rem('host')
    db.rem('port')
    db.dump()

cli()
