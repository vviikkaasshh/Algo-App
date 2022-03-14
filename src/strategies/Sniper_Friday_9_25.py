import logging
from datetime import datetime
import time

from ..instruments.Instruments import Instruments
from ..models.Direction import Direction
from ..models.ProductType import ProductType
from ..strategies.BaseStrategy import BaseStrategy
from ..utils.Utils import Utils
from ..utils.NearestPremium import NearestPremium
from ..trademgmt.Trade import Trade
from ..trademgmt.TradeManager import TradeManager
from ..trademgmt.TradeExitReason import TradeExitReason
from ..trademgmt.TradeState import TradeState

# Each strategy has to be derived from BaseStrategy


class Sniper_Friday_9_25(BaseStrategy):
    __instance = None

    @staticmethod
    def getInstance():  # singleton class
        if Sniper_Friday_9_25.__instance == None:
            Sniper_Friday_9_25()
        return Sniper_Friday_9_25.__instance

    def __init__(self):
        if Sniper_Friday_9_25.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Sniper_Friday_9_25.__instance = self
        # Call Base class constructor
        super().__init__("Sniper_Friday_9_25")
        # Initialize all the properties specific to this strategy
        self.productType = ProductType.MIS
        self.symbols = []
        self.slPercentage = self.GetStopLoss()
        self.targetPercentage = 0
        # When to start the strategy. Default is Market start time
        self.startTimestamp = Utils.getTimeOfToDay(9, 25, 00)
        # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.stopTimestamp = Utils.getTimeOfToDay(10, 15, 0)
        self.squareOffTimestamp = Utils.getTimeOfToDay(
            10, 15, 0)  # Square off time
        # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.capital = 300000
        self.leverage = 0
        # (1 CE + 1 PE) Max number of trades per day under this strategy
        self.maxTradesPerDay = 4
        self.isFnO = True  # Does this strategy trade in FnO or not
        # Applicable if isFnO is True (1 set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)
        self.capitalPerSet = 100000
        self.reEntryMap = {}
        self.IsStrategyCompleted = True
        self.sleepSeconds = 60

    def canTradeToday(self):
        # Should run on Tuesday, Wednesday
        return datetime.now().weekday() in [4]

    def process(self):
        now = datetime.now()
        if now < self.startTimestamp:
            return
        if len(self.trades) >= self.maxTradesPerDay:
            return

        if not self.IsStrategyCompleted and any(self.trades):
            self.CreateReEntryTradeOnSLHit()
            return

        ATMCEStrike, ATMPEStrike = self.GetBNFStrikeBasedOnStraddleWidth()

        ATMCESymbol = Utils.prepareWeeklyOptionsSymbol(
            "BANKNIFTY", ATMCEStrike, 'CE')
        ATMPESymbol = Utils.prepareWeeklyOptionsSymbol(
            "BANKNIFTY", ATMPEStrike, 'PE')
        logging.info('%s: ATMCE = %s, ATMPE = %s',
                     self.getName(), ATMCESymbol, ATMPESymbol)
        # create trades
        self.generateTrades(ATMCESymbol, ATMPESymbol)

    def IsReEntryApplicable(self):
        lastSlHitTrade = self.GetSlHitTrade()
        if lastSlHitTrade is not None:
            if (TradeManager.getLastTradedPrice(lastSlHitTrade.tradingSymbol) < lastSlHitTrade.entry):
                if lastSlHitTrade.tradingSymbol in self.reEntryMap.keys():
                    count = self.reEntryMap[lastSlHitTrade.tradingSymbol]
                    self.reEntryMap[lastSlHitTrade.tradingSymbol] = count + 1
                    logging.info('%s: Re-Entry Count: %f',
                                 self.getName(), self.reEntryMap[lastSlHitTrade.tradingSymbol])
                else:
                    self.reEntryMap[lastSlHitTrade.tradingSymbol] = 1
                    logging.info('%s: Re-Entry Count: %f',
                                 self.getName(), self.reEntryMap[lastSlHitTrade.tradingSymbol])
                return lastSlHitTrade if self.reEntryMap[lastSlHitTrade.tradingSymbol] < 2 else None
        return None

    def CreateReEntryTradeOnSLHit(self):
        slHitTrade = self.IsReEntryApplicable()
        if slHitTrade is not None:
            self.generateTrade(slHitTrade.tradingSymbol, self.calculateLotsPerTrade(
            ), TradeManager.getLastTradedPrice(slHitTrade.tradingSymbol))
            logging.info('%s: Re-Entry Trades generated.', self.getName())
        else:
            logging.info('%s: No Trades Eligible for Re-Entry.',
                         self.getName())

    def GetSlHitTrade(self):
        slHitTrades = [trade for trade in self.trades if trade.endTimestamp is not None and
                       trade.exitReason == TradeExitReason.SL_HIT and trade.orderVersion == self.orderVersion]
        if any(slHitTrades):
            lastSlHitTrade = sorted(
                slHitTrades, key=lambda x: x.endTimestamp, reverse=True)[0]
            IsSameSymbolActiveInTrade = any(
                (trade.tradeState == TradeState.ACTIVE or
                 trade.tradeState == TradeState.CREATED) for trade in self.trades if trade.tradingSymbol == lastSlHitTrade.tradingSymbol
                and trade.orderVersion == self.orderVersion)
            return None if IsSameSymbolActiveInTrade else lastSlHitTrade

    def generateTrades(self, ATMCESymbol, ATMPESymbol):
        numLots = self.calculateLotsPerTrade()
        quoteATMCESymbol = self.getQuote(ATMCESymbol)
        quoteATMPESymbol = self.getQuote(ATMPESymbol)
        if quoteATMCESymbol == None or quoteATMPESymbol == None:
            logging.error(
                '%s: Could not get quotes for option symbols', self.getName())
            return

        self.generateTrade(ATMCESymbol, numLots,
                           quoteATMCESymbol.lastTradedPrice)
        self.generateTrade(ATMPESymbol, numLots,
                           quoteATMPESymbol.lastTradedPrice)

        self.IsStrategyCompleted = False
        logging.info('%s: Trades generated.', self.getName())

    def generateTrade(self, optionSymbol, numLots, lastTradedPrice):
        trade = Trade(optionSymbol)
        trade.strategy = self.getName()
        trade.isOptions = True
        trade.direction = Direction.SHORT  # Always short here as option selling only
        trade.productType = self.productType
        trade.placeMarketOrder = True
        trade.requestedEntry = lastTradedPrice
        # setting this to strategy timestamp
        trade.timestamp = Utils.getEpoch(self.startTimestamp)

        # Get instrument data to know qty per lot
        isd = Instruments.getInstrumentDataBySymbol(optionSymbol)
        trade.qty = isd['lot_size'] * numLots

        trade.stopLoss = Utils.roundToNSEPrice(
            trade.requestedEntry + 30)
        trade.target = Utils.roundToNSEPrice(
            trade.requestedEntry - 60)

        trade.intradaySquareOffTimestamp = Utils.getEpoch(
            self.squareOffTimestamp)
        trade.orderVersion = self.orderVersion
        # Hand over the trade to TradeManager
        TradeManager.addNewTrade(trade)
        self.IsStrategyCompleted = False

    def shouldPlaceTrade(self, trade, tick):
        # First call base class implementation and if it returns True then only proceed
        if super().shouldPlaceTrade(trade, tick) == False:
            return False
        # We dont have any condition to be checked here for this strategy just return True
        return True

    def GetStopLoss(self):
        return 0

    def getTrailingSL(self, trade):
        return 0