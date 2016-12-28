from polyglot.nodeserver_api import Node
from kevoPy import KevoPy
from login import USERNAME, PASSWORD
import hashlib

class KevoDiscovery(Node):

    def __init__(self, *args, **kwargs):
        super(KevoDiscovery, self).__init__(*args, **kwargs)
        self.kevo = KevoPy(USERNAME, PASSWORD)

    def id_2_addr(self, udn):
        ''' convert udn id to isy address '''
        hasher = hashlib.md5()
        hasher.update(udn)
        return hasher.hexdigest()[0:14]

    def discover(self, **kwargs):

        manifest = self.parent.config.get('manifest', {})
        self.parent.poly.logger.info("Discovering Kevo Locks...")
        self.parent.poly.logger.info("User: %s", USERNAME)
        self.kevo.connect()

        self.parent.poly.logger.info("Found %d Locks", len(self.kevo.locks()))

        if len(self.kevo.locks()) > 0:
            for lock in self.kevo.locks():

                name = lock.name()
                address = self.id_2_addr(lock.identifier())

                lnode = self.parent.get_node(address)
                if not lnode:
                    self.logger.info('Adding new Kevo Lock: %s(%s)', name, lock.lock_id)
                    lock = KevoLock(self.parent, self.parent.get_node('kevodisco'), address, lock, manifest)

                    self.parent.locks.append(lock)
                else:
                    self.logger.info('Kevo Lock: %s(%s) already added', name, lock.lock_id)
        else:
            self.logger.info("No Locks found")

        return True

    def query(self, **kwargs):
        self.parent.report_drivers()
        return True

    def refreshAll(self):
        self.kevo.refreshAll(self.parent.report_drivers)

    _drivers = {}

    _commands = {'NETDISCO': discover}

    node_def_id = 'KEVODISCO'

class KevoLock(Node):

    def __init__(self, parent, primary, address, lock, manifest=None):

        lock.parent = self
        self.logger = parent.poly.logger
        self.parent = parent
        self.name = lock.name()
        self.lock = lock
        self.logger.info('Address: %s', address)

        super(KevoLock, self).__init__(parent, address, "Kevo " + lock.name(), primary, manifest)
        self.logger.info('Initializing New Kevo Lock')
        self.update_info()

    def _setOn(self, **kwargs):

        self.logger.info("Locking: %s", self.name)

        result = self.lock.lock()
        if result == True:
            self.report_driver()
            self.logger.info("Locked: %s", self.name)
        else:
            self.logger.info("Locking: %s failed", self.name)

        return result

    def _setOff(self, **kwargs):
        self.logger.info("Locking: %s", self.name)

        result = self.lock.unlock()
        if result == True:
            self.report_driver()
            self.logger.info("Unlocked: %s", self.name)
        else:
            self.logger.info("Unlocking: %s failed", self.name)

        return result


    def _stateToUOM(self, state):
        return {'Unlocked' : 0,
                'Locked'   : 100,
                'Unknown'  : 101,
                'Bolt Jam' : 102,
                'Processing' : 303,
                'Confirming' : 304}[state]

    def query(self, **kwargs):

        self.update_info()
        self.report_driver()
        return True

    def update_info(self):
        self.lock.refresh(self.update_driver)

    def update_driver(self):
        try:
            self.logger.info("Setting ST to %d", self._stateToUOM(self.lock.query()))
            self.set_driver('ST', self._stateToUOM(self.lock.query()))
        except requests.exceptions.ConnectionError as e:
            self.logger.error('Connection error to ISY: %s', e)


    _drivers = {'ST': [0, 11, int]}

    _commands = {'DON': _setOn,
                 'DOF': _setOff,
                 'ST' : query}

    node_def_id = 'KEVO'
