import logging
import time
from datetime import datetime

from ..models.ProductType import ProductType
from ..core.Quotes import Quotes
from ..trademgmt.TradeManager import TradeManager

from ..trademgmt.TradeExitReason import TradeExitReason
from ..utils.Utils import Utils
from ..trademgmt.TradeState import TradeState
from ..telegramlogger.TelegramLogger import Logger, Condition


class BaseStrategy:
    def __init__(self, name):
        # NOTE: All the below properties should be set by the Derived Class (Specific to each strategy)
        self.name = name  # strategy name
        self.enabled = True  # Strategy will be run only when it is enabled
        self.productType = ProductType.MIS  # MIS/NRML/CNC etc
        self.symbols = []  # List of stocks to be traded under this strategy
        self.slPercentage = 0
        self.targetPercentage = 0
        # When to start the strategy. Default is Market start time
        self.startTimestamp = Utils.getMarketStartTime()
        # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.stopTimestamp = None
        self.squareOffTimestamp = None  # Square off time
        # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.capital = 10000
        self.leverage = 1  # 2x, 3x Etc
        self.maxTradesPerDay = 1  # Max number of trades per day under this strategy
        self.isFnO = False  # Does this strategy trade in FnO or not
        # Applicable if isFnO is True (Set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)
        self.capitalPerSet = 0
        # Register strategy with trade manager
        TradeManager.registerStrategy(self)
        # Load all trades of this strategy into self.trades on restart of app
        self.trades = TradeManager.getAllTradesByStrategy(self.name)
        self.strategyStopLoss = 0
        self.orderVersion = 1
        self.sleepSeconds = None
        self.IsStrategyCompleted = True

    def getName(self):
        return self.name

    def isEnabled(self):
        return self.enabled

    def setDisabled(self):
        self.enabled = False

    def process(self):
        # Implementation is specific to each strategy - To defined in derived class
        logging.info("BaseStrategy process is called.")
        pass

    def calculateCapitalPerTrade(self):
        leverage = self.leverage if self.leverage > 0 else 1
        capitalPerTrade = int(self.capital * leverage / self.maxTradesPerDay)
        return capitalPerTrade

    def calculateLotsPerTrade(self):
        if self.isFnO == False:
            return 0
        # Applicable only for fno
        return int(self.capital / self.capitalPerSet)

    def canTradeToday(self):
        # Derived class should override the logic if the strategy to be traded only on specific days of the week
        return True

    def updateStrategyCompleted(self):
        # If strategy has compeleted for first order version
        if self.IsActiveOrderInTrades():
            self.IsStrategyCompleted = False

    def run(self):
        try:
            # NOTE: This should not be overriden in Derived class
            if self.enabled == False:
                logging.warn(
                    "%s: Not going to run strategy as its not enabled.", self.getName())
                return

            if Utils.isMarketClosedForTheDay():
                logging.warn(
                    "%s: Not going to run strategy as market is closed.", self.getName())
                return

            if Utils.isTodayHoliday():
                logging.info(
                    "Cannot start Strategy as Today is Trading Holiday.")
                return

            now = datetime.now()
            if now < Utils.getMarketStartTime():
                Utils.waitTillMarketOpens(self.getName())

            if self.canTradeToday() == False:
                logging.warn(
                    "%s: Not going to run strategy as it cannot be traded today.", self.getName())
                return

            now = datetime.now()
            if now < self.startTimestamp:
                waitSeconds = Utils.getEpoch(
                    self.startTimestamp) - Utils.getEpoch(now)
                logging.info("%s: Waiting for %d seconds till startegy start timestamp reaches...",
                             self.getName(), waitSeconds)
                if waitSeconds > 0:
                    time.sleep(waitSeconds)

            
            self.updateStrategyCompleted()
            # Run in an loop and keep processing
            while True:
                if Utils.isMarketClosedForTheDay():
                    logging.warn(
                        "%s: Exiting the strategy as market closed.", self.getName())
                    break

                if self.stopTimestamp is not None and datetime.now() > self.stopTimestamp:
                    logging.warn(
                        "%s: Exiting the strategy as End time reached", self.getName())
                    break

                # Derived class specific implementation will be called when process() is called
                self.process()

                # Sleep and wake up on every 60th second for Re-Entry Trades
                waitSeconds = self.getWaitSeconds()
                time.sleep(waitSeconds)
        except Exception as e:
            Logger.getInstance().log(self.getName() + " Error " + str(e), Condition.MESSAGE)
            logging.info('%s Error:  %s', self.getName(), str(e))
            raise Exception(str(e))
        finally:
            logging.info("%s: Exiting the strategy from finally",
                         self.getName())

    def getWaitSeconds(self):
        if self.sleepSeconds is not None:
            return self.sleepSeconds - (datetime.now().second % 60)
        return 60 - (datetime.now().second % 60)

    def shouldPlaceTrade(self, trade, tick):
        # Each strategy should call this function from its own shouldPlaceTrade() method before working on its own logic
        if trade == None:
            return False
        if trade.qty == 0:
            TradeManager.disableTrade(trade, 'InvalidQuantity')
            return False

        now = datetime.now()
        if now > self.stopTimestamp:
            logging.info("%s: NoNewTradesCutOffTimeReached: Current time %s, stopTimeStamp %s",
                         self.getName(), str(now), str(self.stopTimestamp))
            TradeManager.disableTrade(trade, 'NoNewTradesCutOffTimeReached')
            return False

        numOfTradesPlaced = TradeManager.getNumberOfTradesPlacedByStrategy(
            self.getName())
        if numOfTradesPlaced >= self.maxTradesPerDay:
            TradeManager.disableTrade(trade, 'MaxTradesPerDayReached')
            return False

        return True

    def addTradeToList(self, trade):
        if trade != None:
            self.trades.append(trade)

    def getQuote(self, tradingSymbol):
        return Quotes.getQuote(tradingSymbol, self.isFnO)

    def getLTP(self, tradingSymbol, isFnO=False):
        return Quotes.getLTP(tradingSymbol, isFnO)

    def getTrailingSL(self, trade):
        return 0

    def MonitorTradeForExpiry(self, trade, tick):
        pass

    def IsAllTradesActive(self):
        activeTrades = [
            trade for trade in self.trades if trade.tradeState == TradeState.ACTIVE]
        return len(activeTrades) > 1

    def SquareOffOnProfit(self):
        pass

    def ExitAllTrades(self):
        tradesToBeExited = [trade for trade in self.trades if trade.tradeState ==
                            TradeState.ACTIVE]

        for trade in tradesToBeExited:
            TradeManager.squareOffTrade(
                trade, TradeExitReason.SQUARE_OFF)
            TradeManager.setTradeToCompleted(
                trade, TradeManager.getLastTradedPrice(trade.tradingSymbol), TradeExitReason.SQUARE_OFF)

        self.stopTimestamp = datetime.now()

    def UpdatePnL(self):
        activeTrades = [
            trade for trade in self.trades if trade.tradeState == TradeState.ACTIVE]
        for trade in activeTrades:
            trade.cmp = TradeManager.symbolToCMPMap[trade.tradingSymbol]
            Utils.calculateTradePnl(trade)

    def GetNearestPossibleNiftyATMSymbol(self, ATMStrike):
        try:
            NiftyATMDict = {}
            previousATMCESymbol = Utils.prepareWeeklyOptionsSymbol(
                "NIFTY", ATMStrike - 50, 'CE')
            previousATMPESymbol = Utils.prepareWeeklyOptionsSymbol(
                "NIFTY", ATMStrike - 50, 'PE')
            nextATMCESymbol = Utils.prepareWeeklyOptionsSymbol(
                "NIFTY", ATMStrike + 50, 'CE')
            nextATMPESymbol = Utils.prepareWeeklyOptionsSymbol(
                "NIFTY", ATMStrike + 50, 'PE')
            currATMCESymbol = Utils.prepareWeeklyOptionsSymbol(
                "NIFTY", ATMStrike, 'CE')
            currATMPESymbol = Utils.prepareWeeklyOptionsSymbol(
                "NIFTY", ATMStrike, 'PE')
            NiftyATMDict[ATMStrike - 50] = abs(self.getLTP(
                previousATMCESymbol, True) - self.getLTP(previousATMPESymbol, True))
            NiftyATMDict[ATMStrike + 50] = abs(self.getLTP(
                nextATMCESymbol, True) - self.getLTP(nextATMPESymbol, True))
            NiftyATMDict[ATMStrike] = abs(self.getLTP(
                currATMCESymbol, True) - self.getLTP(currATMPESymbol, True))
            if abs(NiftyATMDict[min(NiftyATMDict, key=NiftyATMDict.get)] - NiftyATMDict[ATMStrike]) > 3:
                return min(NiftyATMDict, key=NiftyATMDict.get)
            else:
                return ATMStrike
        except Exception as e:
            logging.info(
                '%s: Could not get Nearest ATM for option symbols', self.getName())
            return ATMStrike

    def IsOneLegStoplosshit(self):
        return any(((trade.exitReason == TradeExitReason.SL_HIT) or (trade.exitReason ==
                   TradeExitReason.TRAIL_SL_HIT)) and self.orderVersion == trade.orderVersion
                   for trade in self.trades)

    def IsActiveOrderInTrades(self):
        return any((trade.tradeState == TradeState.ACTIVE and self.orderVersion == trade.orderVersion)
                   for trade in self.trades)

    def GetBNFStrikeBasedOnStraddleWidth(self, straddleWidth = 0.5):
        bankNiftySymbol = 'NIFTY BANK'
        lastTradedPrice = self.getLTP(bankNiftySymbol, isFnO=False)
        if lastTradedPrice == None:
            logging.error('%s: Could not get quote for %s',
                          self.getName(), bankNiftySymbol)
            return

        ATMStrike = Utils.getNearestStrikePrice(lastTradedPrice, 100)
        ATMCESymbol = Utils.prepareWeeklyOptionsSymbol(
            "BANKNIFTY", ATMStrike, 'CE')
        ATMPESymbol = Utils.prepareWeeklyOptionsSymbol(
            "BANKNIFTY", ATMStrike, 'PE')
        logging.info('%s: ATMCE = %s, ATMPE = %s',
                     self.getName(), ATMCESymbol, ATMPESymbol)
        
        quoteATMCESymbol = self.getQuote(ATMCESymbol)
        quoteATMPESymbol = self.getQuote(ATMPESymbol)

        if quoteATMCESymbol == None or quoteATMPESymbol == None:
            logging.error(
                '%s: Could not get quotes for option symbols', self.getName())
            return

        totalStraddlePrice = quoteATMCESymbol.lastTradedPrice + quoteATMPESymbol.lastTradedPrice
        ATMCEStrike =  Utils.getNearestStrikePrice(ATMStrike + (straddleWidth * totalStraddlePrice), 100)
        ATMPEStrike =  Utils.getNearestStrikePrice(ATMStrike - (straddleWidth * totalStraddlePrice), 100)
        logging.info('%s: Straddle width %f ATMCEStrike: %s ATMPEStrike: %s', self.getName(),
                straddleWidth, ATMCEStrike, ATMPEStrike)
        return ATMCEStrike, ATMPEStrike
