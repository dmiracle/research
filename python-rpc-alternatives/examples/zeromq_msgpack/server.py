import msgpack
import zmq

ctx = zmq.Context()
sock = ctx.socket(zmq.REP)
sock.bind("tcp://*:5555")
print("ZeroMQ msgpack server listening on 5555")

while True:
    req = msgpack.loads(sock.recv(), raw=False)
    if req.get("method") == "add":
        a, b = req.get("params", [0, 0])
        sock.send(msgpack.dumps({"result": a + b}))
    else:
        sock.send(msgpack.dumps({"error": "unknown method"}))
