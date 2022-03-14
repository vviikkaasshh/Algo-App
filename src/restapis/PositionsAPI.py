from flask.views import MethodView
import json
import logging
from ..core.Controller import Controller

from ..core.Quotes import Quotes
from ..utils.Utils import Utils

class PositionsAPI(MethodView):
  def get(self):
    brokerHandle = Controller.getBrokerLogin().getBrokerHandle()
    positions = brokerHandle.positions()
    logging.info('User positions => %s', positions)
    return json.dumps(positions)