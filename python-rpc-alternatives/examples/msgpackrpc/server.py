from msgpackrpc import Address, Server

def add(a, b):
    return a + b

if __name__ == "__main__":
    server = Server({"add": add})
    server.listen(Address("0.0.0.0", 7001))
    print("Msgpack-RPC server listening on 7001")
    server.start()
