from flask import *
from flask_restful import *
import io, os
import json
from flask_cors import CORS

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)




# Root path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
img = os.listdir(ROOT_DIR + "/static/data/img")
imgData = os.listdir(ROOT_DIR + "/static/data/imgData")


def writeJsonToFile(data, imageDataName):
    imgDataPath = app.root_path + "/static/data/imgData/"
    filePath = os.path.join(imgDataPath, imageDataName + '.json')
    with io.open(filePath, 'wb') as outfile:
        outfile.write((json.dumps(data)))

    return filePath


def loadJsonFileToData(imageDataName):
    imgDataPath = app.root_path + "/static/data/imgData/"
    filePath = os.path.join(imgDataPath, imageDataName + '.json')
    if os.path.exists(filePath):
        with io.open(filePath) as jsonData:
            return json.load(jsonData)
    else:
        return []

class images(Resource):
    def get(self):
        print "send img info"
        return img


class currentImageForUser(Resource):
    def get(self):
        return ""


class imageData(Resource):
    def get(self, imageDataName):
        return loadJsonFileToData(imageDataName)

    def put(self, imageDataName):

        data = request.data
        if data:
            dataDict = json.loads(data)

            # Write in disk
            writeJsonToFile(dataDict, imageDataName)
            #         TODO: merge data. Create file.





api.add_resource(images, '/images')
api.add_resource(imageData, '/imageData/<string:imageDataName>')



@app.route('/')
def index():
    return "Hello"





