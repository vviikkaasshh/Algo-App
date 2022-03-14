from enum import Enum
import requests


class Condition(Enum):
    WARNING = "⚠️"
    MESSAGE = "💬"
    INFO = "📟"

class Logger:
    __instance = None
    TOKEN = ""
    CHAT_ID = "" 
    @staticmethod
    def getInstance():  # singleton class
        if Logger.__instance == None:
            Logger(Logger.TOKEN, Logger.CHAT_ID)
        return Logger.__instance

    def __init__(self, token, chat_id):
        if Logger.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Logger.__instance = self
        self._token = token
        self._chat_id = chat_id
        self._url = f"https://api.telegram.org/bot{token}/"

    def log(self, message, condition = None):
        text = message
        if condition is not None:
            text = f"{condition.value} {message}"
        url = self._url  + "sendMessage"
        response = requests.post(
            url = url,
            params = {
                "chat_id": self._chat_id,
                "text": text
            }
        )
        response.raise_for_status()

    def warning(self, message):
        self.log(message, Condition.WARNING)

    def info(self, message):
        self.log(message, Condition.INFO)

    def message(self, message):
        self.log(message, Condition.MESSAGE)