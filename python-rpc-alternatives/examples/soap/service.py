from spyne import Application, ServiceBase, rpc, Integer
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

class Calculator(ServiceBase):
    @rpc(Integer, Integer, _returns=Integer)
    def add(ctx, a, b):  # noqa: N805 (Spyne naming)
        return a + b

if __name__ == "__main__":
    app = Application([Calculator], "calc.soap", in_protocol=Soap11(), out_protocol=Soap11())
    wsgi_app = WsgiApplication(app)
    server = make_server("0.0.0.0", 8000, wsgi_app)
    print("SOAP server on 8000; WSDL at http://localhost:8000/?wsdl")
    server.serve_forever()
