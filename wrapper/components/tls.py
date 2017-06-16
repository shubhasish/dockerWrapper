from os.path import expanduser
import docker.tls as tls

DEFAULT_HOME_PATH = expanduser('~') + '/.docker/machine/machines/%s/'
CA_PATH = DEFAULT_HOME_PATH + 'ca.pem'
CERT_PATH = DEFAULT_HOME_PATH + 'cert.pem'
KEY_PATH = DEFAULT_HOME_PATH + 'key.pem'



class TLS:

    def __init__(self):
        pass

    def getTLSconfig(self,name):
        return tls.TLSConfig(client_cert=(CERT_PATH%name,KEY_PATH%name))
