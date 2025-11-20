import jsonrpclib

if __name__ == "__main__":
    client = jsonrpclib.Server("http://localhost:4000")
    print("2 + 5 =", client.add(2, 5))
