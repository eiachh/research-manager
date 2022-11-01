from glob import glob
import json
import math
from common_lib.const import constants
from flask import Flask,request

class researchManager():
    def __init__(self):
        self.request_data = ''

    def getPrefferedResearchJson(self):
        return {'Result': 'None'}

resManager = researchManager()

port = 5003
app = Flask(__name__)

@app.route('/get_prefered_research', methods=['GET'])
def getPreferedResearchEndpoint():
    resManager.request_data = request.get_json()
    respData = resManager.getPrefferedResearchJson()
    return respData

@app.route('/ready', methods=['GET'])
def getReadiness():
    return "{Status: OK}"

app.run(host='0.0.0.0', port=port)