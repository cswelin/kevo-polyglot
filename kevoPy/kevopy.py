# -*- coding: utf-8 -*-
import requests
import re
import json
import time
import websocket
import threading
from kevolock import KevoLock

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class KevoPy(object):
    LOCK_STATUS_CHANGE = "LockStatus"

    _username = ''
    _password = ''
    _host = ''
    _websocketLocation = ''
    _ws = None
    _wst = None

    _loginPath  = 'login'
    _signinPath = 'signin'
    _wsLocationPath = 'user/remote_locks/auth/show.json'
    _locks       = {}

    def __init__(self, username, password, host='https://www.mykevo.com/'):

        self._username   = username
        self._password   = password

        self._host       = host
        self._session    = requests.Session()

    def _reteiveToken(self):

        response = self._session.get(self._host + self._loginPath, verify=False)
        # response = self._session.get(self._host + self._loginPath, verify=False)
        # print response
        responseText = response.text

        if response.url.endswith("user/locks"):
            return False

        # print response.url
        p = re.compile(r'input name="authenticity_token".*?value=\"(.*?)\"', re.MULTILINE | re.DOTALL)
        values = re.findall(p, responseText)

        self._token = values[0].strip()

        return True

    def _parseLockIdentifiers(self,html):

        p = re.compile(r'<div class=\'lock_unlock_container\' data-bolt-state=\'.*?\' data-lock-id=\'(.*?)\' id', re.MULTILINE | re.DOTALL)
        # print html
        values = re.findall(p, html)

        # print html
        for value in values:
            kevo = KevoLock(value.strip(), self._session, self._host)
            kevo.refresh()
            self._locks[kevo.lock_id] = kevo

    def _parseWebsocketLocation(self):

        try:
            r = self._session.get(self._host + self._wsLocationPath)
            self._websocketLocation = json.loads(r.text)["socket_location"]
            return True
        except Exception as e:
            print(e)

    def _openSocketConnection(self, *args):
        if self._ws is not None:
            self._ws.close()
            self._wst.join()

        self.logger.info("BEFORE")
        self._ws = websocket.WebSocketApp(self._websocketLocation, on_message = self._on_message, on_error = self._on_error, on_close = self._on_close)
        self._ws.on_open = self._on_open
        self._wst = threading.Thread(target=self._ws.run_forever)
        self._wst.daemon = True
        self._wst.start()
        self.logger.info("BEFORE AFTER")

    def _on_message(self, ws, message):
        data = json.loads(message)

        self.logger.info(data)
        print(data)
        if data["messageType"] == self.LOCK_STATUS_CHANGE:
            self._handleLockStatusMessage(data)

    def _on_error(self, ws, error):
        print(error)

    def _on_close(self, ws):
        self.logger.info("### closed ###")
        print("### closed ###")

        time.sleep(5)
        self.openSocketConnection()

    def _on_open(self, ws):
        self.logger.info("### opened ####")
        print("### connection open ###")

    def _handleLockStatusMessage(self, message):
        data = message["messageData"]

        if "command" in data:
            self._handleCommand(data["command"])
        else:
            self._handleLockStatus(data)

        print data

    def _handleLockStatus(self, data):
        kevoLock = self._locks[data["lockId"]]
        kevoLock.setState(self._statusForState(data["boltState"]))

    def _handleCommand(self, lock_id, data):
        status = self._statusForCommand(data["type"], data["status"])

        kevoLock = self._locks[lock_id]
        kevoLock.setStatus(status)
        if status == "Locked" or status == "Unlocked":
            kevoLock.setState(status)

    def _statusForCommand(self, command, state):
        if command == 1:
            return ["Unknown", "Submitted", "Connecting", "Connected", "Processing", "Locked"][state]
        elif command == 2:
            return ["Unknown", "Submitted", "Connecting", "Connected", "Processing", "Unlocked"][state]
        else:
            return ["Unknown", "Submitted", "Connecting", "Connected", "Processing", "Unknown", "Updating", "Confirming"][state]


    def _statusForState(self, state):
        if state in ["Locked", "lock", 1]:
            return "Locked"
        elif state in ["Unlocked", "unlock", 2]:
            return "Unlocked"
        else:
            return "Unknown"

    def login(self):

        if self._reteiveToken():

            r = self._session.post(self._host + self._signinPath,

            data={"user[username]"      : self._username,
                 "user[password]"       : self._password,
                 "authenticity_token"   : self._token,
                 "commit"               : "Sign In",
                 "utf8"                 : "✓"})

            self._parseLockIdentifiers(r.text)

            if self._parseWebsocketLocation():
                self._openSocketConnection()

    def locks(self):
        return self._locks.values()

    def refreshAll(self, completion = None):
        self.login()
        for lock in self._locks.values():
            self.logger.info("Refreshing")
            lock.refresh(completion)

def main():

    websocket.enableTrace(True)
    kevo = KevoPy('user', 'pass')
    kevo.login()

    while True:
        for lock in kevo.locks():
            print lock.query()

        time.sleep(30)


if __name__ == '__main__':
    main()
