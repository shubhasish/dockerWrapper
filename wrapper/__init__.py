from wrapper.components import machine

m = machine.Machine(path="/usr/local/bin/docker-machine")
print m.ls()
# client = docker.DockerClient(**m.config(machine='default'))
# client.ping()