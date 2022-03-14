import logging

from ..core.Quotes import Quotes
from ..utils.Utils import  Utils

class NearestPremium:

    @staticmethod
    def GetBNFNearestPremiumSymbol(nearestPremium, symbol_type):
        ltp = Quotes.getLTP("NIFTY BANK", False)
        ATMStrike = Utils.getNearestStrikePrice(ltp, 100)

        symbol_map = {}
        ATMCESymbolLtp = None
        while ATMCESymbolLtp == None or not NearestPremium.IsvalidMapForValues(nearestPremium, symbol_map):
                ATMCESymbol = Utils.prepareWeeklyOptionsSymbol(
                    "BANKNIFTY", ATMStrike, symbol_type)
                ATMCESymbolLtp = Quotes.getLTP(ATMCESymbol, True)
                if ATMCESymbolLtp > nearestPremium:
                    if symbol_type == "CE":
                        ATMStrike = ATMStrike + 100
                    elif symbol_type == "PE":
                        ATMStrike = ATMStrike - 100                  
                elif ATMCESymbolLtp < nearestPremium:
                    if symbol_type == "CE":
                        ATMStrike = ATMStrike - 100
                    elif symbol_type == "PE":
                        ATMStrike = ATMStrike + 100
                symbol_map[ATMCESymbol] = ATMCESymbolLtp
            
        return NearestPremium.closest(symbol_map, nearestPremium)

    @staticmethod
    def closest(dict_map, value):
        keyValue = min(dict_map.items(), key=lambda x: abs(value - x[1]))
        logging.info("Nearest Premium: Symbol: %s LTP: %f", keyValue[0], keyValue[1])      
        return keyValue[0]
    
    @staticmethod
    def IsvalidMapForValues(nearestPremium, dict_map: dict):
        IsLesserPresent = any(val < nearestPremium for val in dict_map.values())
        IsGreaterPresent = any(val > nearestPremium for val in dict_map.values())

        if IsLesserPresent and IsGreaterPresent:
            return True
        return False