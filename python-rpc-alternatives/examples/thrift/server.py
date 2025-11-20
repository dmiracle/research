import thriftpy2
from thriftpy2.rpc import make_server

calculator_thrift = thriftpy2.load("calculator.thrift", module_name="calculator_thrift")

class CalculatorHandler:
    def add(self, a, b):
        return a + b

if __name__ == "__main__":
    server = make_server(calculator_thrift.Calculator, CalculatorHandler(), "0.0.0.0", 9090)
    print("Thrift server listening on 9090")
    server.serve()
