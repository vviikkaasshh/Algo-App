from flask.views import MethodView
import json
from flask import render_template, request
from ..core.Controller import Controller
from datetime import datetime
import os
from json2html import *
import json
attributes = ["exchange", "isFutures", "isOptions", "optionType", "placeMarketOrder", "intradaySquareOffTimestamp", "timestamp",
              "createTimestamp", "startTimestamp", "endTimestamp"]


class TradeStatusAPI(MethodView):
    def get(self):
        html = None
        args = request.args
        filePath = os.path.abspath(
            'src/trades/' + str(datetime.now().date()) + '/trades.json')
        with open(filePath, 'r') as f:
            content = f.read()
            dict_obj = json.loads(content)
            return json.dumps(dict_obj)
            html = json2html.convert(
                json=json.dumps(deleteAttributes(dict_obj)))
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


def deleteAttributes(dict_col):
    for obj in dict_col:
        for attr in attributes:
            obj.pop(attr, None)
    return dict_col
