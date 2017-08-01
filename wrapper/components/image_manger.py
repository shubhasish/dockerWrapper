from flask_restful import Resource
from flask import request, Response
from docker import APIClient
from modules.tls import TLS
import ast

class ImageBuilder(Resource):
    def get(self):
        return "Wrong Method, Use POST instead"

    def put(self):
        file = request.files['dockerfile']
        file.save('Dockerfile')
        tls = TLS()
        tlsConfig = tls.getTLSconfig('master')
        cli = APIClient(base_url="tcp://192.168.99.101:2376",tls=tlsConfig)
        def build_stream():
            for line in cli.build(path="/home/subhasishp/IOT/iotdatapipeline/",dockerfile="ignite_dockerfile",stream=True,rm=True,tag="latest"):
                m = ast.literal_eval(line)
                print m
                if "error" in m:
                    yield m['error']
                else:

                    yield str(m)

        return Response(build_stream(),mimetype='text/xml')
