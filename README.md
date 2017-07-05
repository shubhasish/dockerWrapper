# dockerWrapper
This a docker orchestartion, deployment and container management tool. It can be used to automate the provisioning, swarm creation and orchestration, deployment management and monitoring.
This Application uses 'docker-machine', docker SDK and docker API to automate your all tasks.

## Pre-Requisite
You need to have docker, docker-machine installed on your machine to make this application get going.

## Usage
This application will be used for:
1. Provisioning
2. Swarm Creation
3. Deployment
4. Monitoring
5. Auto-Scaling

## Components

### Poperty file

It's a JSON file, where we will be mentioning all our provisioning requirements and ask to **wrapper** application to automate that.  of the nodes to be created will be mentioned in **config.json** file.
There should be separate JSON files for every swarm cluster created. This application can be used for provisioning of different types of drivers like virtualbox, AWS, digitalOcean etc. Since this application uses **docker-machine** for provisioning purpose,
therefore it supports all drivers that are being supported the  **docker-machine**. For details refer:
                                ```https://docs.docker.com/machine/drivers/```

Format of the JSON file is <name of machine>:<properties of machine>

Properties are mentioned in the json file in a  key:value fashion. Default properties are:
1. role: Can be manager/slave
2. driver: Type of driver

Other properties depends on the type of driver, which can be found on **docker-machine** documentation page. Example, for virtualbox refer:
                            ```https://docs.docker.com/machine/drivers/virtualbox/#options```

Mention the options in a key:value fashion, removing the driver prefix from the option.
For example,

**--virtualbox-memory** will be **"memory":<value>** in JSON file

**--virtualbox-cpu-count** will be **"cpu-count":<value>** in JSON file

Example of a JSON file:

```
{
  "master": {
    "role": "manager",
    "driver": "virtualbox",
    "memory": 1024,
    "cpu-count": 1
  },
  "worker": {
    "driver": "virtualbox",
    "role": "slave"
  }
}
```

### Composer Folder
Place your deployment scripts **docker-compose.yaml** in your composer folder. The application will deploy it for you.