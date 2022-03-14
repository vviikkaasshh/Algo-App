from flask.views import MethodView
import json
import logging
import threading
from flask import send_from_directory, render_template, request
import os
from datetime import datetime

from ..config.Config import getSystemConfig
from ..core.Algo import Algo
from ..trademgmt.TradeManager import  TradeManager

class StrategyAPI(MethodView):
  def post(self):
    # start strategy by Name
    return json.dumps(False)

  def put(self):
    # Stop strategy by Name
    strategy_name = request.args["name"]
    if strategy_name not in TradeManager.strategyToInstanceMap.keys() or not strategy_running(strategy_name):
          return json.dumps(False)
    strategyInstance = TradeManager.strategyToInstanceMap[strategy_name]
    strategyInstance.ExitAllTrades()
    return json.dumps(True)

  def get(self):
    #get TradeManager
    strategies_dict = {}
    for thread_name in TradeManager.strategyToInstanceMap.keys():
          strategies_dict[thread_name] = strategy_running(thread_name)
    return json.dumps(strategies_dict)

def strategy_running(name):
  return name in [thread.name for thread in threading.enumerate()]