import os
import logging
from flask import Flask, session
from datetime import datetime
from flask_cors import CORS

from .config.Config import getBrokerAppConfig, getServerConfig, getSystemConfig
from .restapis.HomeAPI import HomeAPI
from .restapis.BrokerLoginAPI import BrokerLoginAPI
from .restapis.StartAlgoAPI import StartAlgoAPI
from .restapis.PositionsAPI import PositionsAPI
from .restapis.HoldingsAPI import HoldingsAPI
from .restapis.TradeStatusAPI import TradeStatusAPI
from .restapis.PnLAPI import PnLAPI
from .restapis.OrderAPI import OrderAPI
from .restapis.LoginAPI import LoginAPI
from .restapis.StrategyAPI import StrategyAPI
from .restapis.MarginAPI import MarginAPI

app = Flask(__name__)
CORS(app)
app.secret_key = 'super secret key'
app.config['DEBUG'] = True

app.add_url_rule("/", view_func=HomeAPI.as_view("home_api"))
app.add_url_rule("/apis/broker/login/zerodha", view_func=BrokerLoginAPI.as_view("broker_login_api"))
app.add_url_rule("/apis/algo/start", view_func=StartAlgoAPI.as_view("start_algo_api"))
app.add_url_rule("/positions", view_func=PositionsAPI.as_view("positions_api"))
app.add_url_rule("/holdings", view_func=HoldingsAPI.as_view("holdings_api"))
app.add_url_rule("/tradeStatus", view_func=TradeStatusAPI.as_view("trade_status_api"))
app.add_url_rule("/pnlStatus", view_func=PnLAPI.as_view("pnl_api"))
app.add_url_rule("/order", view_func=OrderAPI.as_view("order_api"))
app.add_url_rule("/login", view_func=LoginAPI.as_view("LoginAPI"))
app.add_url_rule("/strategy", view_func=StrategyAPI.as_view("StrategyAPI"))
app.add_url_rule("/margin", view_func=MarginAPI.as_view("MarginAPI"))

def initLoggingConfg(filepath):
  format = "%(asctime)s: %(message)s"
  logging.basicConfig(filename=filepath, format=format, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

# Execution starts here
serverConfig = getServerConfig()

deployDir = serverConfig['deployDir']
if os.path.exists(deployDir) == False:
  print("Deploy Directory " + deployDir + " does not exist. Exiting the app.")
  exit(-1)

logFileDir = serverConfig['logFileDir']
if os.path.exists(logFileDir) == False:
  print("LogFile Directory " + logFileDir + " does not exist. Exiting the app.")
  exit(-1)

print("Deploy  Directory = " + deployDir)
print("LogFile Directory = " + logFileDir)
initLoggingConfg(logFileDir + "/app_" + str(datetime.now().date()) + ".log")

logging.info('serverConfig => %s', serverConfig)

brokerAppConfig = getBrokerAppConfig()
logging.info('brokerAppConfig => %s', brokerAppConfig)

port = serverConfig['port']
print(port)

if __name__ == "__main__":
    # Run app
    app.run(host="0.0.0.0", port=80)