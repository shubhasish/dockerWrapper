#### Help Contents

MAIN_HELP = "Usage: wrapper COMMAND\n" \
            "A docker swarm orchestration and managemnet tool\n\n" \
            "Commands\n\n" \
            "create\t\t create/provisoning a single node or a group of nodes\n" \
            "swarmit\t\t initialize swarm and create a cluster\n" \
            "deploy\t\t deploy a single component or the whole stack into the swarm cluster\n" \
            "redeploy\t re-deploy/Update a single component of the whole application stack\n" \
            "wrapup\t\t cleans the whole workspce and stops watching or managing the swarm cluster\n" \
            "monitor\t\t streams cluster statistics to any time series database\n" \
            "help\t\t list down all option\n\n" \
            "For more information use 'wrapper COMMAND --help'"


DEPLOY_HELP = "Usage: wrapper deploy [OPTIONS] <service-name>/all \n\n" \
              "Command to deploy a single service or multiple services to the cluster\n\n" \
              "Options\n\n" \
              "-p --path\t\t path to the docker-compose '.yml or .yaml' file\n" \
              "<service-name>\t\t name of service to be deployed\n" \
              "all           \t\t deploy all services to the cluster"

WRAPUP_HELP = "Usage: wrapper wrapUp [OPTIONS] <node>/all \n\n" \
              "Command to remove a single node or multiple nodes from the cluster\n\n" \
              "Options\n\n" \
              "all\t\t remove the whole cluster and clean-up the workspace\n" \
              "<node>\t\t name of the node to be removed"

CREATE_HELP = "Usage: wrapper create [OPTIONS] \n\n" \
              "Command to create a cluster\n\n" \
              "Options\n\n" \
              "-p --path\t\t path to JSON config file\n"

SWARMIT_HELP = "Usage: wrapper swarmit [OPTIONS]\n\n" \
               "Command to create a swarm cluster\n\n" \
               "Option\n\n"

REDEPLOY_HELP = "Usage: wrapper redeploy [OPTIONS] <service-name>\n\n" \
                "Command to redploy a service\n\n" \
                "Options\n\n" \
                "-p --path\t\t path to the docker-compose '.yml or .yaml' file"

PATH_ERROR = "Not a valid file path or File path not provided. \nPlease provide a valid path or file." \


