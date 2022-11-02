from glob import glob
import json
import math
from common_lib.const import constants
from common_lib.utilities import utilities
from flask import Flask,request

class researchManager():


    def __init__(self):
        self.request_data = ''

    def createResponseJson(self, ogameId):
        if(ogameId == -1):
            return {'researchManager' : {'researchable' : {'researchID' : -1, 'researchLevel' : -1}}}

        researchLevel = self.request_data['researchLevels'][constants.convertOgameIDToAttrName(ogameId)]
        return {'researchManager' : {'researchable' : {'researchID' : ogameId, 'researchLevel' : researchLevel}}}

    def getPrefferedResearchJson(self):
        availableResearches = self.getAvailableResearches()
        preferredResearchItem = self.getPreferredResearch(availableResearches)
        if(preferredResearchItem is None):
            return self.createResponseJson(-1)
        return self.createResponseJson(preferredResearchItem['id'])

    def prioritySortBy(item):
        return item['priorityValue']

    def getPreferredResearch(self, availableResearches):
        researchPriorityList = self.sortResearchesByPriority()
        resWeights = self.getResourceWeightsFromAllowance()

        sortedResearchPriorityList = []
        for research in availableResearches:
            priceJson = self.request_data['researchPrices'][constants.convertOgameIDToAttrName(research)]
            priceInWeightedUnits = utilities.getResourceSumInUnitPrice(priceJson, resWeights['m'], resWeights['c'], resWeights['d'])
            if(research in researchPriorityList):
                sortedResearchPriorityList.append({'priorityValue' : researchPriorityList.index(research) + 1, 'id' : research, 'priceInUnits' : priceInWeightedUnits})

        sortedResearchPriorityList = sorted(sortedResearchPriorityList, key=researchManager.prioritySortBy)
        
        if(len(sortedResearchPriorityList) == 0):
            return None

        selectedResearch = sortedResearchPriorityList[0]
        for comparingItem in sortedResearchPriorityList:
            if(not self.isOriginalWeightedPriorityValueBetter(selectedResearch, comparingItem)):
                selectedResearch = comparingItem
        return selectedResearch

    def isOriginalWeightedPriorityValueBetter(self, originalItem, comparingItem):
        priorityDiff = comparingItem['priorityValue'] - originalItem['priorityValue']
        priorityDiffWeight = 1 + 0.10 * priorityDiff

        adjustedPrice = comparingItem['priceInUnits'] * priorityDiffWeight
        if( originalItem['priceInUnits'] > adjustedPrice):
            return False
        return True
    #TODO make researchPriorityList not static but based on current state of the bot
    def sortResearchesByPriority(self):
        
        researchPriorityList = [constants.WEAPON_TECH, constants.SHIELD_TECH, constants.ARMOUR_TECH, constants.SPY_TECH, constants.IMPULSE_DRIVE, constants.COMBUSTION_DRIVE, constants.COMPUTER_TECH,
                                constants.HYPERSPACE_DRIVE, constants.HYPER_SPACE_TECH, constants.PLASMA_TECH, constants.ASTROPHYSICS]
        return researchPriorityList

    def getResourceWeightsFromAllowance(self):
        #expected 1:2:3 -> 3k metal = 1.5k crystal = 1k deu
        metalUnitPrice = 1

        availableMetal = self.request_data['allowanceResources']['Metal']
        availableCrystal = self.request_data['allowanceResources']['Crystal']
        availableDeuterium = self.request_data['allowanceResources']['Deuterium']

        crystalAdjustedUnitPrice = availableMetal / availableCrystal
        deuAdjustedUnitPrice = availableMetal / availableDeuterium

        return {'m' : metalUnitPrice, 'c' : crystalAdjustedUnitPrice, 'd' : deuAdjustedUnitPrice}

    def isResearchAffordable(self, odameId):
        attrNameOfResearch = constants.convertOgameIDToAttrName(odameId)
        researchPrices = self.request_data['researchPrices']

        allowance = self.request_data['allowanceResources']

        if(researchPrices[attrNameOfResearch]['Metal'] >  allowance['Metal']):
            return False
        if(researchPrices[attrNameOfResearch]['Crystal'] >  allowance['Crystal']):
            return False
        if(researchPrices[attrNameOfResearch]['Deuterium'] >  allowance['Deuterium']):
            return False
        return True

    def getAvailableResearches(self):
        availableResearchesByID = []
        for researchId in constants.ogameIdOfAllResearch:
            if(utilities.isPrerequisiteMet(researchId, self.request_data) and self.isResearchAffordable(researchId)):
                availableResearchesByID.append(researchId)
        return availableResearchesByID

resManager = researchManager()

port = 5003
app = Flask(__name__)

@app.route('/get_preferred_research', methods=['GET'])
def getPreferedResearchEndpoint():
    resManager.request_data = request.get_json()
    respData = resManager.getPrefferedResearchJson()
    return respData

@app.route('/ready', methods=['GET'])
def getReadiness():
    return "{Status: OK}"

#def my_foofoo(item):
#    return item['key']
#
#mylist = [{'key': 2}, {'key': 3}, {'key': 4}]
#sorted(mylist, key=researchManager.prioritySortBy)


app.run(host='0.0.0.0', port=port)