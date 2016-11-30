from flask import *
from flask_restful import *
from flask_cors import CORS
import os, io, json, random

app = Flask(__name__)
app.debug = True

cors = CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

# Root path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
img = os.listdir(ROOT_DIR + "/static/data/img")
imgData = os.listdir(ROOT_DIR + "/static/data/imgData")


def writeJsonToFile(data, imageDataName, dir):
    imgDataPath = app.root_path + dir
    filePath = os.path.join(imgDataPath, imageDataName + '.json')
    with io.open(filePath, 'wb') as outfile:
        outfile.write((json.dumps(data)))

    return filePath


def loadJsonFileToData(imageDataName, dir):
    imgDataPath = app.root_path + dir
    filePath = os.path.join(imgDataPath, imageDataName + '.json')
    if os.path.exists(filePath):
        with io.open(filePath) as jsonData:
            return json.load(jsonData)
        return []
    else:
        pass


class Batch:
    def __init__(self):
        self.batches = loadJsonFileToData('batch', "/static/data/")

    def generateBatchs(self, size):
        # Clear the batch
        self.batches = []

        # Even Chunk
        def chunkIt(seq, num):
            avg = len(seq) / float(num)
            out = []
            last = 0.0

            while last < len(seq):
                out.append(seq[int(last):int(last + avg)])
                last += avg

            return out

        imgChunckedResults = chunkIt(img, size)

        # Write in Json data in to file
        for imgChunckedResult in imgChunckedResults:
            batchObj = {
                'files': imgChunckedResult,
                'current': {
                    'imageAnnotator': 0,
                    'objectAnnotator': 0
                },
                'total': len(imgChunckedResult),
                'annotator': ''
            }
            self.batches.append(batchObj)
        self.save()

        return self.batches

    def userCurrentBatch(self, type, userid):

        for batchObj in self.batches:
            if (self.ifBatchInProgress(batchObj, type) and (batchObj['annotator'] == userid)):
                return batchObj
        return self.assignBatchByUser(userid)

    def ifBatchCompleted(self, batchObj, type):
        return batchObj['current'][type] == (batchObj['total'] - 1)

    def ifBatchInProgress(self, batchObj, type):
        return batchObj['current'][type] < (batchObj['total'] - 1)

    def userBatchProgress(self, type, userid):
        batchObj = self.userCurrentBatch(type, userid)
        return float(batchObj['current'][type] + 1) / float(batchObj['total'])

    def userBatchProgressUpdate(self, type, userid, value):
        # TODO: Test this
        batchObj = self.userCurrentBatch(type, userid)
        for index, targetObj in enumerate(self.batches):
            if targetObj == batchObj:
                batchObj['current'][type] = int(value)
                self.batches[index] = batchObj
                self.save()
                return float(batchObj['current'][type] + 1) / float(batchObj['total'])

    def assignBatchByUser(self, userid):
        # Change ONLY one batchObj

        for index, batchObj in enumerate(self.batches):
            if batchObj['annotator'] == '':
                batchObj['annotator'] = userid
                self.batches[index] = batchObj
                self.save()
                return batchObj

    def save(self):
        writeJsonToFile(self.batches, 'batch', "/static/data/")


# Api
# Classes



class images(Resource):
    def get(self):
        return img


class userCurrentBatch(Resource):
    # Batch images
    def get(self):
        headers = request.headers
        if headers:
            userid = headers['userid']
            type = headers['type']
            batch = Batch()
            return batch.userCurrentBatch(type, userid)


class currentImageForUser(Resource):
    def get(self):
        return ""


class imageData(Resource):
    def get(self, imageDataName):
        return loadJsonFileToData(imageDataName, "/static/data/imgData/")

    def put(self, imageDataName):
        data = request.data
        if data:
            dataDict = json.loads(data)

            # Write in disk
            writeJsonToFile(dataDict, imageDataName, "/static/data/imgData/")
            #         TODO: merge data. Create file.


class imageQuikCategory(Resource):
    def get(self, imageDataName):
        return loadJsonFileToData(imageDataName, "/static/data/quikCategory/")

    def put(self, imageDataName):
        data = request.data
        if data:
            dataOld = loadJsonFileToData(imageDataName, "/static/data/quikCategory/")

            dataDict = json.loads(data)
            category = dataDict.keys()[0]
            existed = False
            for idx, val in enumerate(dataOld):

                if category in val.keys():
                    # If the category existed
                    existed = True
                    # overwrite
                    dataOld[idx] = dataDict
                    break

            # Write in disk
            if (existed == False):
                # Create New
                dataOld.append(dataDict)
            writeJsonToFile(dataOld, imageDataName, "/static/data/quikCategory/")


class generateBatchs(Resource):
    def put(self):
        data = request.data
        if data:
            dataDict = json.loads(data)
            size = dataDict['size']
            batch = Batch()
            return batch.generateBatchs(size)


class userBatchPrograss(Resource):
    def get(self):
        headers = request.headers
        if headers:
            userid = headers['userid']
            type = headers['type']
            batch = Batch()
            return batch.userBatchProgress(type, userid)

    def put(self):
        data = request.data
        if data:
            dataDict = json.loads(data)
            userid = dataDict['userid']
            type = dataDict['type']
            value = dataDict['value']
            batch = Batch()
            return batch.userBatchProgressUpdate(type, userid, value)


api.add_resource(images, '/images')
api.add_resource(imageData, '/imageData/<string:imageDataName>')
api.add_resource(imageQuikCategory, '/imageQuikCategory/<string:imageDataName>')
api.add_resource(generateBatchs, '/batch/generateBatchs')
api.add_resource(userBatchPrograss, '/batch/userBatchPrograss')
api.add_resource(userCurrentBatch, '/batch/userCurrentBatch')


@app.route('/')
def index():
    return "Hello"
