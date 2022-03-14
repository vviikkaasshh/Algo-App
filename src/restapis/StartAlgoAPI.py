from flask.views import MethodView
import json
import logging
import threading
from flask import send_from_directory, render_template, request
import os
from datetime import datetime

from ..config.Config import getSystemConfig
from ..core.Algo import Algo

filePath = os.path.abspath('src/app_' + str(datetime.now().date()) + '.log')

class StartAlgoAPI(MethodView):
  def post(self):
    # start algo in a separate thread
    x = threading.Thread(target=Algo.startAlgo, name="Algo Running")
    x.start()
    systemConfig = getSystemConfig()
    homeUrl = systemConfig['homeUrl'] + '?algoStarted=true'
    logging.info('Sending redirect url %s in response', homeUrl)
    respData = { 'redirect': homeUrl }
    return json.dumps(respData)

  def get(self):
        #get TradeManager
        return Algo.updateTrade(request.args["tradeId"])