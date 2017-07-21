import json
import requests
import time

class KevoLock(object):

    _lock_data  = {}
    _unlock     = 'user/remote_locks/command/remote_unlock.json?arguments='
    _lock       = 'user/remote_locks/command/remote_lock.json?arguments='
    _info       = 'user/remote_locks/command/lock.json?arguments='
    _session    = ''
    _host       = ''

    def __init__(self, lock_id, session, host, on_update = None):
        self.lock_id = lock_id
        self.on_update = on_update
        self._session = session
        self._host = host

    def refresh(self, completion = None):
        r = self._session.get(self._host + self._info + self.lock_id)
        self._lock_data =  json.loads(r.text)

        if completion is not None:
            completion()

    def name(self):
        return self._lock_data["name"]

    def identifier(self):
        return self._lock_data["id"]

    def query(self):
        return self._lock_data["bolt_state"]

    def status(self):
        return self._lock_data["bolt_status"]

    def setState(self, state):
        self._lock_data["bolt_state"] = state
        self._callback()

    def setStatus(self, status):
        self._lock_data["bolt_status"] = state
        self._callback()

    def unlock(self):
        try:

            self._expected_state = "Unlocked"
            self._previous_lock_state = self._lock_data["bolt_state"]

            r = self._session.get(self._host + self._unlock + self.lock_id)
            return self.verifyConfirmation()

        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, TypeError) as e:

            return False

    def lock(self):
        try:

            self._expected_state = "Locked"
            self._previous_lock_state = self._lock_data["bolt_state"]

            r = self._session.get(self._host + self._lock + self.lock_id)
            return self.verifyConfirmation()

        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, TypeError) as e:

            return False

    def toggle(self):
        if self.query() == "Unlocked":
            self.lockLock()
        else:
            self.unlockLock()


    def verifyConfirmation(self):
        timeout = time.time() + 60*2
        while self._expected_state != self._lock_data["bolt_state"]:

            if time.time() > timeout:
                return False

            time.sleep(15)

            self.refresh()

        self._callback()
        return True

    def _callback(self):
        if self.on_update is not None:
            self.on_update()
