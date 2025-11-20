from msgpackrpc import Address, Client

if __name__ == "__main__":
    client = Client(Address("localhost", 7001))
    print("2 + 5 =", client.call("add", 2, 5))
