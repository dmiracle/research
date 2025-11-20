import capnp

calculator_capnp = capnp.load("calculator.capnp")

if __name__ == "__main__":
    client = capnp.TwoPartyClient(("localhost", 7000))
    calc = client.bootstrap().cast_as(calculator_capnp.Calculator)
    resp = calc.add(2, 5).wait()
    print("2 + 5 =", resp.result)
