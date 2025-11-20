import rpyc
from rpyc.utils.server import ThreadedServer

class CalculatorService(rpyc.Service):
    def exposed_add(self, a, b):
        return a + b

if __name__ == "__main__":
    server = ThreadedServer(CalculatorService, port=18861, protocol_config={"allow_public_attrs": True})
    print("RPyC server listening on 18861")
    server.start()
