from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector
from polykevo_types import KevoDiscovery, KevoLock

VERSION = "0.1.1"

class KevoNodeServer(SimpleNodeServer):

    controller = []
    locks = []

    def setup(self):
        super(KevoNodeServer, self).setup()

        self.poly.logger.info('Config File param: %s', self.poly.configfile)

        try:
            manifest = self.config.get('manifest',{})

            KevoDiscovery(self,'kevodisco','Kevo Discovery', True, manifest)

            self.controller = self.get_node('kevodisco')
            self.controller.discover()
            self.update_config()

        except TypeError as e:
            self.parent.poly.logger.info('KevoNodeServer setup caught exception: %s', e)

    def poll(self):
        try:
            self.poly.logger.info("poll")
            self.report_drivers()

        except TypeError as e:
            self.parent.poly.logger.info('KevoNodeServer setup caught exception: %s', e)

    def long_poll(self):
        try:
            self.poly.logger.info("long_poll")
            if len(self.locks) >= 1:
                self.controller.refreshAll()

        except TypeError as e:
            self.parent.poly.logger.info('KevoNodeServer long_poll caught exception: %s', e)

    def report_drivers(self):
        try:
            self.poly.logger.info("report_drivers")

            if len(self.locks) >= 1:
                for lock in self.locks:
                    lock.update_driver()
        except TypeError as e:
            self.parent.poly.logger.info('KevoNodeServer report_drivers caught exception: %s', e)

def main():

    poly = PolyglotConnector()

    nserver = KevoNodeServer(poly, 5, 60)
    poly.connect()
    poly.wait_for_config()

    poly.logger.info("Kevo Interface version " + VERSION + "created")
    nserver.setup()

    poly.logger.info("Setup completed. Running Server.")

    nserver.run()


if __name__ == "__main__":
    main()
