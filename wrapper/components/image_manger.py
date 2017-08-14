from flask_restful import Resource
from flask import request, Response
from docker import APIClient
import pickledb
from config import DM_URL
from config import WRAPPER_DB_PATH
from config import DOCKER_FILE_PATH
from modules.machine import Machine
import json
from flask_restful import Resource
from flask import Response
from config import getClient

from modules.tls import TLS
import ast

class ImageBuilder(Resource):
    def get(self):
        return 'Wrong Method, Use POST instead'

    def template(self):
        self.SERVERS = dict()
        self.manager = Machine(path=DM_URL)
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH, False)
            self.SERVERS = self.db.get('servers')
        except Exception as e:
            pass

    def put(self):
        file = request.files['dockerfile']
        file.save(DOCKER_FILE_PATH + 'Dockerfile')
        self.template()
        image = request.form['image']
        imageName = '127.0.0.1:5000/%s:latest'%image
        if not self.SERVERS:
            response = str({'status':'failure','message':'Check if you have already initialized cluster'})
            return Response(response, mimetype='text/xml')
        self.registry = [x for x in self.SERVERS.keys() if x == 'registry'][0]
        tls = TLS()
        tlsConfig = tls.getTLSconfig(self.registry)
        cli = APIClient(base_url=self.SERVERS[self.registry]['url'],tls=tlsConfig)
        imagesList =[x['RepoTags'][0] for x in cli.images()]

        if imageName in imagesList:
            try:
                cli.remove_image(imageName)
            except Exception as e:
                return Response({'status':'failure','message':str(e.message)})
        def build_stream():
            for line in cli.build(path=DOCKER_FILE_PATH,dockerfile='Dockerfile',stream=True,rm=True,tag=imageName):
                if 'error' in line:
                    yield {'status':'failure','message':json.loads(line)['error']}
                else:
                    jsonObject = json.loads(line)

                    for x in jsonObject.keys():
                        if x == 'progressDetail' :
                            continue
                        else:
                            yield jsonObject[x]
                            yield '\n'
                # yield line
        return Response(build_stream(),mimetype='application/json')

class ImagePusher(Resource):
    def get(self):
        return 'Wrong Method, Use POST instead'

    def template(self):
        self.SERVERS = dict()
        self.manager = Machine(path=DM_URL)
        try:
            self.db = pickledb.load(WRAPPER_DB_PATH, False)
            self.SERVERS = self.db.get('servers')
        except Exception as e:
            pass

    def post(self):
        requestJson = request.get_json()
        image = requestJson['image']
        self.template()
        if not self.SERVERS:
            return Response('Check if you have already initialized cluster', mimetype='text/xml')
        self.registry = [x for x in self.SERVERS.keys() if x == 'registry'][0]
        tls = TLS()
        tlsConfig = tls.getTLSconfig(self.registry)
        cli = APIClient(base_url=self.SERVERS[self.registry]['url'],tls=tlsConfig)
        imagesList =[x['RepoTags'][0] for x in cli.images()]
        def image_pusher():
            if image in imagesList:
                push = cli.push(image,stream=True)
                for line in  push:
                    if 'error' in line:
                        yield {'status':'failure','message':json.loads(line)['error']}
                    else:
                        jsonObject = json.loads(line)
                        for x in jsonObject.keys():
                            if x == 'progressDetail':
                                continue
                            else:
                                yield jsonObject[x]
                                yield '\n'

            else:
                yield {'status':'failure','message':'No such Image Found'}
        return Response(image_pusher(),mimetype='application/json')