from flask.views import MethodView
from flask import request, jsonify
from ..core.Controller import Controller
import logging

from ..core.Quotes import Quotes
from ..utils.Utils import Utils
from ..telegramlogger.TelegramLogger import Logger

SEGMENT_CONST = 'segment'
NIFTY_50 = 'NIFTY 50'
BANK_NIFTY = 'NIFTY BANK'


class MarginAPI(MethodView):
    def get(self):
        responses = []
        brokerHandle = Controller.getBrokerLogin().getBrokerHandle()
        segment = 'equity'
        if SEGMENT_CONST in request.args:
            segment = request.args[SEGMENT_CONST]
        response = brokerHandle.margins(segment)
        current_margin = response['net']
        responses.append(response)

        orders = get_orders()
        basket_order_response = brokerHandle.basket_order_margins(orders)
        required_margin = basket_order_response['initial']['total']
        logging.info('%s: Current Margin: %s Required Margin: %s',
                     'MarginAPI', current_margin, required_margin)
        Logger.getInstance().message(f'Current Margin: {current_margin} Required Margin: {required_margin}')
        responses.append(basket_order_response)
        return jsonify(responses)


def get_orders():
    orders = []

    ltp = Quotes.getLTP(NIFTY_50)
    ATMStrike = Utils.getNearestStrikePrice(ltp)
    ATMCESymbol = Utils.prepareWeeklyOptionsSymbol(
        'NIFTY', ATMStrike, 'CE')

    order = {
        "exchange": "NFO",
        "tradingsymbol": "NIFTY2230316600CE",
        "transaction_type": "SELL",
        "variety": "regular",
        "product": "NRML",
        "order_type": "MARKET",
        "quantity": 200,
        "price": 0,
        "trigger_price": 0
    }
    order['tradingsymbol'] = ATMCESymbol
    orders.append(order)

    ATMPESymbol = Utils.prepareWeeklyOptionsSymbol(
        'NIFTY', ATMStrike, 'PE')

    order = {
        "exchange": "NFO",
        "tradingsymbol": "NIFTY2230316600CE",
        "transaction_type": "SELL",
        "variety": "regular",
        "product": "NRML",
        "order_type": "MARKET",
        "quantity": 200,
        "price": 0,
        "trigger_price": 0
    }
    order['tradingsymbol'] = ATMPESymbol
    orders.append(order)

    ltp = Quotes.getLTP(BANK_NIFTY)
    ATMStrike = Utils.getNearestStrikePrice(ltp, 100)
    ATMCESymbol = Utils.prepareWeeklyOptionsSymbol(
        'BANKNIFTY', ATMStrike, 'CE')
    order = {
        "exchange": "NFO",
        "tradingsymbol": "NIFTY2230316600CE",
        "transaction_type": "SELL",
        "variety": "regular",
        "product": "NRML",
        "order_type": "MARKET",
        "quantity": 75,
        "price": 0,
        "trigger_price": 0
    }
    order['tradingsymbol'] = ATMCESymbol
    orders.append(order)

    ATMPESymbol = Utils.prepareWeeklyOptionsSymbol(
        'BANKNIFTY', ATMStrike, 'PE')
    order = {
        "exchange": "NFO",
        "tradingsymbol": "NIFTY2230316600CE",
        "transaction_type": "SELL",
        "variety": "regular",
        "product": "NRML",
        "order_type": "MARKET",
        "quantity": 75,
        "price": 0,
        "trigger_price": 0
    }
    order['tradingsymbol'] = ATMPESymbol
    orders.append(order)
    return orders
