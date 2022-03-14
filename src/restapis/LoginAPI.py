from flask.views import MethodView
import json
from ..config.Config import *
import logging
from flask import session, request, jsonify
from ..telegramlogger.TelegramLogger import Logger, Condition
logged_inUsers = []

class LoginAPI(MethodView):
    def post(self):
        try:
            _json = request.json
            _username = _json['username']
            _password = _json['password']

            # validate the received values
            if _username and _password:
                # check user exists
                users = getUsersAppConfig()
                is_valid = any(user for user in users if users[0]["username"] ==
                            _username and users[0]["password"] == _password)

                if is_valid:
                    logged_inUsers.append(_username)
                    return jsonify({'message': 'You are logged in successfully'})
                else:
                    logging.info("LoginAPI: Bad Request - invalid password")
                    Logger.getInstance().log("LoginAPI: Bad Request - invalid password", Condition.MESSAGE)
                    resp = jsonify(
                        {'message': 'Bad Request - invalid password'})
                    resp.status_code = 400
                    return resp
            else:
                logging.info("LoginAPI: Bad Request - invalid credendtials")
                Logger.getInstance().log("LoginAPI: Bad Request - invalid password", Condition.MESSAGE)
                resp = jsonify(
                    {'message': 'Bad Request - invalid credendtials'})
                resp.status_code = 400
                return resp

        except Exception as e:
            logging.info("LoginAPI: %s", str(e))
            Logger.getInstance().log("LoginAPI: " + str(e), Condition.MESSAGE)

    def get(self):
        username = request.args["username"]
        if username in logged_inUsers:
            return jsonify({'message': 'You are already logged in', 'username': username})
        else:
            resp = jsonify({'message' : 'Unauthorized'})
            resp.status_code = 401
            return resp

    def delete(self):
        username = request.args["username"]
        if username in logged_inUsers:
            logged_inUsers.remove(username)
            return jsonify({'message': 'You successfully logged out'})
