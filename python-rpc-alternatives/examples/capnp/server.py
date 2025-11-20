import capnp

calculator_capnp = capnp.load("calculator.capnp")

class Calculator(calculator_capnp.Calculator.Server):
    def add(self, a, b, _context, **_kwargs):
        return a + b

if __name__ == "__main__":
    server = capnp.TwoPartyServer(("localhost", 7000), bootstrap=Calculator())
    print("Cap'n Proto server listening on 7000")
    server.listen()
