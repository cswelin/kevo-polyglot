# -*- coding: utf-8 -*-
import requests
import re
import json
import time

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class KevoPy(object):

    _username = ''
    _password = ''
    _host = ''

    _loginPath  = 'login'
    _signinPath = 'signin'

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
    def _praseLockIdentifiers(self,html):

        p = re.compile(r'<div class=\'lock_unlock_container\' data-bolt-state=\'.*?\' data-lock-id=\'(.*?)\' id', re.MULTILINE | re.DOTALL)
        # print html
        values = re.findall(p, html)

        # print html
        for value in values:
            kevo = KevoLock(value.strip(), self._session, self._host)
            kevo.refresh()
            self._locks[kevo.lock_id] = kevo

    def connect(self):

        if self._reteiveToken():

            r = self._session.post(self._host + self._signinPath,

            data={"user[username]"      : self._username,
                 "user[password]"       : self._password,
                 "authenticity_token"   : self._token,
                 "commit"               : "Sign In",
                 "utf8"                 : "✓"})

            self._praseLockIdentifiers(r.text)

    def locks(self):
        return self._locks.values()

    def refreshAll(self, completion = None):
        self.connect()
        for lock in self._locks.values():
            self.logger.info("Refreshing")
            lock.refresh(completion)


class KevoLock(object):

    _lock_data  = {}
    _unlock     = 'user/remote_locks/command/remote_unlock.json?arguments='
    _lock       = 'user/remote_locks/command/remote_lock.json?arguments='
    _info       = 'user/remote_locks/command/lock.json?arguments='
    _session    = ''
    _host       = ''

    def __init__(self, lock_id, session, host):

        self.lock_id = lock_id
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

        self.parent.update_driver()
        return True

def main():

    kevo = KevoPy('user', 'pass')
    kevo.connect()

    for lock in kevo.locks():
        print lock.query()


if __name__ == '__main__':
    main()
