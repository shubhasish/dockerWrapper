# dockerWrapper
This a python application designed to automate the swarm creation process and orchestration purpose.

## Usage
This application will be used for:
1. Swarm Creation
2. Composer Management
3. Load Balancing
4. Auto Scalaing

### Poperty file
The properties of the nodes to be created will be mentioned in **config.json** file.
There should be a single **config.json** file for each swarm cluster. Mention the server's name, it's role and the driver in the config file the appplication will take care of the rest.
If new servers or any change are added to the, the application will detect the changes and work on those changes only.

Formatt of the config file **name:<property>**
```
{
  "master": {
    "role": "manager",
    "driver": "virtualbox"
  },
  "worker": {
    "driver": "virtualbox",
    "role": "slave"
  }
}
```
### Composer Folder
Place your deployment scripts **docker-compose.yaml** in your composer folder. The application will deploy it for you.