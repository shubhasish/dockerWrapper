from flask_restful import Resource
from flask import request
from docker import APIClient
from modules.tls import TLS

class ImageBuilder(Resource):
    def get(self):
        return "Wrong Method, Use POST instead"

    def put(self):
        file = request.files['dockerfile']
        file.save('Dockerfile')
        tls = TLS()
        tlsConfig = tls.getTLSconfig('master')
        cli = APIClient(base_url="tcp://192.168.99.101:2376",tls=tlsConfig)
        for line in cli.build(path="/home/subhasishp/IOT/iotdatapipeline/",dockerfile="Dockerfile",stream=True,rm=True,tag="latest"):
            print line
        return "ok"