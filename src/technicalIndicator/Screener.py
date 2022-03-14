from datetime import datetime as dt
from datetime import timedelta
from ..utils.Utils import Utils
import logging
import pandas as pd
import time

from ..core.Controller import Controller
from ..instruments.Instruments import Instruments
from .CandlePattern import *
from ..telegramlogger.TelegramLogger import Logger, Condition


class Screener:
    tickers = ["NIFTY 50", "NIFTY BANK", "SBIN", "TCS", "VEDL", "MARUTI", "ICICIBANK", "HINDUNILVR",
               "HDFCBANK", "HCLTECH", "DRREDDY", "BAJFINANCE", "BAJAJ-AUTO", "AXISBANK", "ASHOKLEY"
               "TECHM"]

    __instance = None

    @staticmethod
    def getInstance():  # singleton class
        if Screener.__instance == None:
            Screener()
        return Screener.__instance

    def __init__(self):
        if Screener.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Screener.__instance = self
        self.Name = "Screener"
        self.kite = Controller.getBrokerLogin().getBrokerHandle()

    def getName(self):
        return self.Name

    def run(self):
        try:
            now = dt.now()
            if now < Utils.getMarketStartTime():
                Utils.waitTillMarketOpens(self.getName())
            while Utils.isMarketOpen():
                for ticker in self.tickers:
                    self.GiveSignificance(ticker)
                time.sleep(301 - (dt.now().second % 60.0)) # 300 second interval between each new execution
            # for ticker in self.tickers:
            #     self.GiveSignificance(ticker)
            logging.info(
                "%s: Market is closed for today", self.getName())
        except Exception as e:
            logging.error("%s: Error  occured %s", self.getName(), str(e))

    def GiveSignificance(self, ticker):
        try:
            ohlc = self.fetchOHLC(ticker, '5minute', 5)
            ohlc = ohlc.iloc[:-1,:]
            ohlc_day = self.fetchOHLC(ticker, 'day', 30)
            ohlc_day = ohlc_day.iloc[:-1, :]
            cp = candle_pattern(ohlc, ohlc_day)
            logging.info("%s: %s %s", self.Name, ticker, cp)
            if "Significance - H" in cp and "Pattern - None" not in cp:
                Logger.getInstance().log(ticker + " " + cp, Condition.MESSAGE) 
        except Exception as e:
            print(str(e) + "skipping for ", ticker)

    def fetchOHLC(self, ticker, interval, duration):
        """extracts historical data and outputs in the form of dataframe"""
        instrument = Instruments.getInstrumentDataBySymbol(ticker)
        data = pd.DataFrame(self.kite.historical_data(
            instrument['instrument_token'], dt.today()- timedelta(duration),dt.today(), interval))
        data.set_index("date", inplace=True)
        return data
