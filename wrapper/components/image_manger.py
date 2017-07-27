from flask_restful import Resource
from flask import request


class ImageBuilder(Resource):
    def get(self):
        return "Wrong Method, Use POST instead"

    def post(self):
        requestJson = request.files
        file = open('/home/subhasishp/Dockerfile','w+')
        print type(requestJson)
        #for lines in requestJson:
        #    file.write(lines)
        file.close()
        #content = requestJson['image']
        print requestJson
        return "ok"