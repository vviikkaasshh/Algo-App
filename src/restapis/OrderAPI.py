from flask.views import MethodView
import json
import logging
import threading
from flask import send_from_directory, render_template, request
import os
from datetime import datetime

from ..config.Config import getSystemConfig
from ..core.Algo import Algo
from ..trademgmt.TradeManager import TradeManager

class OrderAPI(MethodView):
  def post(self):
    # start algo in a separate thread
    is_nifty = False
    is_short = False
    if "is_nifty" in request.args:
          is_nifty = True
    if "is_short" in request.args:
          is_short = True
    
    strategyInstance = TradeManager.strategyToInstanceMap["Order_Placer"]
    if strategyInstance != None:
        strategyInstance.place_order(not is_nifty, not is_short)
    
    return json.dumps(str(True))

  def put(self):
        #get TradeManager
        is_processed = False
        stoploss_value = int(request.args["value"])
        strategyInstance = TradeManager.strategyToInstanceMap["Order_Placer"]
        if strategyInstance != None:
              is_processed = strategyInstance.set_stoploss(stoploss_value)
        return json.dumps(str(is_processed))
  
  def delete(self):
        #get TradeManager
        is_processed = False
        strategyInstance = TradeManager.strategyToInstanceMap["Order_Placer"]
        if strategyInstance != None:
              is_processed = strategyInstance.exit_order()
        return json.dumps(str(is_processed))