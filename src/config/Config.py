import json
import os


def getServerConfig():
    abs_file_path = os.path.abspath('src/AppConfig/server.json')
    with open(abs_file_path, 'r') as server:
        jsonServerData = json.load(server)
        jsonServerData["logFileDir"] = os.path.abspath('src/')
        jsonServerData["deployDir"] = os.path.abspath('src/')
        return jsonServerData


def getSystemConfig():
    abs_file_path = os.path.abspath('src/AppConfig/system.json')
    with open(abs_file_path, 'r') as system:
        jsonSystemData = json.load(system)
        return jsonSystemData


def getBrokerAppConfig():
    abs_file_path = os.path.abspath('src/AppConfig/brokerapp.json')
    with open(abs_file_path, 'r') as brokerapp:
        jsonUserData = json.load(brokerapp)
        return jsonUserData


def getUsersAppConfig():
    abs_file_path = os.path.abspath('src/AppConfig/users.json')
    with open(abs_file_path, 'r') as brokerapp:
        jsonUserData = json.load(brokerapp)
        return jsonUserData


def getHolidays():
    abs_file_path = os.path.abspath('src/AppConfig/holidays.json')
    with open(abs_file_path, 'r') as holidays:
        holidaysData = json.load(holidays)
        return holidaysData


def getTimestampsData():
    serverConfig = getServerConfig()
    timestampsFilePath = os.path.join(
        serverConfig['deployDir'], 'timestamps.json')
    if os.path.exists(timestampsFilePath) == False:
        return {}
    timestampsFile = open(timestampsFilePath, 'r')
    timestamps = json.loads(timestampsFile.read())
    return timestamps


def saveTimestampsData(timestamps={}):
    serverConfig = getServerConfig()
    timestampsFilePath = os.path.join(
        serverConfig['deployDir'], 'timestamps.json')
    with open(timestampsFilePath, 'w') as timestampsFile:
        json.dump(timestamps, timestampsFile, indent=2)
    print("saved timestamps data to file " + timestampsFilePath)
