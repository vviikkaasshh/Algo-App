from flask.views import MethodView
import json
import logging
import threading
from flask import send_from_directory
from flask import render_template, request
import os
from datetime import datetime

from ..config.Config import getSystemConfig
from ..core.Algo import Algo
from pathlib import Path
from json2html import *


class PnLAPI(MethodView):
    def get(self):
        args = request.args
        filePath = os.path.abspath(
            'src/trades/')
        files = sorted(Path(filePath).glob("**/*.json"),
                       key=lambda x: x, reverse=True)
        profitLoss = 0
        travesalDepth = 1

        if "pnlDays" in args and args["pnlDays"].isdigit():
            travesalDepth = int(args["pnlDays"])

        html = None
        if "byDay" in args:
            dict_obj = CalculatePnLByDay(files[0:travesalDepth])
        else:
            dict_obj = CalculatePnLByStrategy(files[0:travesalDepth])
        
        html = json2html.convert(
            json=json.dumps(dict_obj))
        return """<style>
table {
    		    font-family: arial, sans-serif;
    		    border-collapse: collapse;
    		    width: 100%;
    		}
    		td, th {
    		    border: 1px solid #dddddd;
    		    text-align: left;
    		    padding: 8px;
    		}

</style>"""+html


def CalculatePnL(filePath):
    with open(filePath, 'r') as f:
        content = f.read()
        dict_obj = json.loads(content)
        val = 0
        for trade in dict_obj:
            val += float(trade["pnl"])
        return val


def CalculatePnLByStrategy(filePaths):
    strategyDict = {}
    for filePath in filePaths:
        with open(filePath, 'r') as f:
            content = f.read()
            dict_obj = json.loads(content)
            for trade in dict_obj:
                if trade["strategy"] in strategyDict.keys():
                    strategyDict[trade["strategy"]
                                 ] = strategyDict[trade["strategy"]] + float(trade["pnl"])
                else:
                    strategyDict[trade["strategy"]] = float(trade["pnl"])
    strategyDict["Final PnL"] = sum(strategyDict.values())
    return strategyDict

def CalculatePnLByDay(filePaths):
    import re
    dateRegex = re.compile(r'\d{4}-\d{2}-\d{2}')
    format = '%Y-%m-%d'
    dayName = {}
    for filePath in filePaths:
        with open(filePath, 'r') as f:
            mo = dateRegex.search(str(filePath))
            # convert from string format to datetime format
            date = datetime.strptime(mo.group(), format)
            content = f.read()
            dict_obj = json.loads(content)
            for trade in dict_obj:
                if date.strftime("%A") in dayName.keys():
                    dayName[date.strftime("%A")
                                 ] = dayName[date.strftime("%A")] + float(trade["pnl"])
                else:
                    dayName[date.strftime("%A")] = float(trade["pnl"])
    dayName["Final PnL"] = sum(dayName.values())
    return dayName
