import thriftpy2
from thriftpy2.rpc import make_client

calculator_thrift = thriftpy2.load("calculator.thrift", module_name="calculator_thrift")

if __name__ == "__main__":
    with make_client(calculator_thrift.Calculator, "localhost", 9090) as client:
        print("2 + 5 =", client.add(2, 5))
