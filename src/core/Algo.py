import logging
import threading
import time

from ..instruments.Instruments import Instruments
from ..trademgmt.TradeManager import TradeManager
from ..trademgmt.TradeState import TradeState
from ..trademgmt.TradeExitReason import TradeExitReason

from ..strategies.Sniper_Friday_9_25 import Sniper_Friday_9_25
#from Test import Test


class Algo:
    isAlgoRunning = None

    @staticmethod
    def startAlgo():
        if "Trade-Manger" not in [thread.name for thread in threading.enumerate()]:
            Algo.isAlgoRunning = False
        if Algo.isAlgoRunning == True:
            logging.info("Algo has already started..")
            return

        logging.info("Starting Algo...")
        Instruments.fetchInstruments()

        # start trade manager in a separate thread
        tm = threading.Thread(target=TradeManager.run, name="Trade-Manger")
        tm.start()

        # sleep for 2.5 seconds for TradeManager to get initialized and read file
        time.sleep(10)

        # start running strategies: Run each strategy in a separate thread
        threading.Thread(target=Sniper_Friday_9_25.getInstance(
        ).run, name="Sniper_Friday_9_25").start()
        
        Algo.isAlgoRunning = True
        logging.info("Algo started.")

    @staticmethod
    def updateTrade(tradeID):
        if any(TradeManager.trades):
            trade = next(
                targetTrade for targetTrade in TradeManager.trades if targetTrade.tradeID == tradeID)
            if trade is not None:
                TradeManager.squareOffTrade(trade, TradeExitReason.MANUAL)
                TradeManager.setTradeToCompleted(
                    trade, TradeManager.getLastTradedPrice(trade.tradingSymbol), TradeExitReason.MANUAL)
                logging.info('Trade Id status updated: %s', tradeID)
                return str(True)
            else:
                logging.info('Trade Id status not in Trades list: %s', tradeID)
        return str(False)
