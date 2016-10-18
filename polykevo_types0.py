from polyglot.nodeserver_api import Node
from kevoPy import KevoPy
from login import USERNAME, PASSWORD

class KevoDiscovery(Node):

    def __init__(self, *args, **kwargs):
        super(KevoDiscovery, self).__init__(*args, **kwargs)
        self.kevo = KevoPy(USERNAME, PASSWORD)
        self.kevo.logger = self.parent.poly.logger


    def discover(self, **kwargs):

        manifest = self.parent.config.get('manifest', {})
        self.parent.poly.logger.info("Discovering Kevo Locks...")
        self.parent.poly.logger.info("User: %s", USERNAME)
        self.kevo.connect()

        self.logger.info("Found %d Locks", len(self.kevo.locks()))

        if len(self.kevo.locks()) > 0:
            for lock in self.kevo.locks():
                name = lock.name()
                identifier = lock.identifier()[0:13]

                lnode = self.parent.get_node(identifier)
                if not lnode:
                    self.logger.info('Adding new Kevo Lock: %s(%s)', name, lock.lock_id)
                    self.parent.locks.append(KevoLock(self.parent, identifier, self.parent.get_node('KEVODISCO'), lock, manifest))
                else:
                    self.logger.info('Kevo Lock: %s(%s) already added', name, lock.lock_id)
        else:
            self.logger.info("No Locks found")

        return True

    def query(self, **kwargs):
        self.parent.report_drivers()
        return True

    def refreshAll(self):
        self.kevo.refreshAll()

    _drivers = {}

    _commands = {'NETDISCO': discover}

    node_def_id = 'KEVODISCO'

class KevoLock(Node):

    def __init__(self, parent, address, primary, lock, manifest=None):

        self.parent = parent
        self.logger = self.parent.poly.logger
        self.name = lock.name()
        self.lock = lock

        super(KevoLock, self).__init__(parent, address, "Kevo " + lock.name(), primary, manifest)

        self.logger.info('Initializing New Kevo Lock')
        self.update_info()

    def _setOn(self, **kwargs):
        self.lock.lock()

    def _setOff(self, **kwargs):
        self.lock.unlock()

    def _stateToUOM(self, state):
        return {'Unlocked' : 0,
                'Locked'   : 100,
                'Unknown'  : 101,
                'Bolt Jam' : 102}[state]

    def query(self, **kwargs):
        self.update_info()
        self.report_driver()
        return True

    def update_info(self):
        try:
            self.lock.refresh()
            self.logger.info("Setting ST to %d", self._stateToUOM(self.lock.query()))
            self.set_driver('ST', self._stateToUOM(self.lock.query()))
        except requests.exceptions.ConnectionError as e:
            self.logger.error('Connection error to ISY: %s', e)



    _drivers = {'ST': [0, 11, int]}

    _commands = {'DON': _setOn,
                 'DOF': _setOff,
                 'ST' : query,
                 'QUERY': query}

    node_def_id = 'KEVO'
