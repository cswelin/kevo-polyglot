from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector
from polykevo_types import KevoDiscovery, KevoLock

VERSION = "0.1.0"

class KevoNodeServer(SimpleNodeServer):

    controller = []
    locks = []

    def setup(self):
        super(KevoNodeServer, self).setup()
        manifest = self.config.get('manifest',{})

        self.controller = KevoDiscovery(self,'disco','Kevo Discovery', True, manifest)
        # self.poly.logger.info("FROM Poly ISYVER: " + self.poly.isyver)
        self.controller.discover()
        self.update_config()

        # self.nodes['kevocontrol'].discover()

    def poll(self):
        self.poly.logger.info("poll")
        if len(self.locks) >= 1:
            self.controller.refreshAll()


    def long_poll(self):
        self.poly.logger.info("long_poll")
        if len(self.locks) >= 1:
            self.controller.refreshAll()


    def report_drivers(self):
        self.poly.logger.info("report_drivers")

        if len(self.controller.locks()) >= 1:
            for lock in self.locks:
                lock.update_driver()


def main():

    poly = PolyglotConnector()

    nserver = KevoNodeServer(poly, 20, 40)
    poly.connect()
    poly.wait_for_config()

    poly.logger.info("Kevo Interface version " + VERSION + "created")
    nserver.setup()

    poly.logger.info("Setup completed. Running Server.")

    nserver.run()


if __name__ == "__main__":
    main()
