import msgpack
import zmq

ctx = zmq.Context()
sock = ctx.socket(zmq.REQ)
sock.connect("tcp://localhost:5555")
sock.send(msgpack.dumps({"method": "add", "params": [2, 5]}))
resp = msgpack.loads(sock.recv(), raw=False)
print(resp)
