from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

def add(a, b):
    return a + b

if __name__ == "__main__":
    server = SimpleJSONRPCServer(("0.0.0.0", 4000))
    server.register_function(add)
    print("JSON-RPC server listening on 4000")
    server.serve_forever()
