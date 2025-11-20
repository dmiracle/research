# Python RPC Alternatives to REST/gRPC

This survey looks at Python-friendly RPC approaches beyond REST and gRPC. It favors protocols that cover different transport and schema philosophies, notes recent GitHub activity (system clock is 2025-11-20), and ships runnable examples. All setup uses `uv` for environment and package management.

## Quick comparison
- **Apache Thrift (thriftpy2)** (Apache-2.0; last push 2025-11-19; ~10k stars): IDL-driven binary RPC, strong cross-language story, mature.
- **JSON-RPC (jsonrpclib)** (Apache-2.0; last push 2025-11-09; ~55 stars): Lightweight HTTP-friendly RPC using JSON messages.
- **RPyC** (NOASSERTION; last push 2025-08-14; ~1.6k stars): Transparent remote object access; great for Python-Python control channels.
- **ZeroMQ REQ/REP with msgpack** (BSD; last push 2025-11-17; ~4k stars): Message socket pattern; you design the contract, very fast.
- **Cap'n Proto (pycapnp)** (BSD-2; last push 2025-10-23; ~500 stars): Schema-first zero-copy messages with built-in RPC.
- **Msgpack-RPC** (no license metadata; last push 2021-11-27; ~200 stars): Thin RPC over msgpack; project appears inactive.
- **SOAP via Spyne/Zeep** (NOASSERTION; last push 2025-09-15; ~2k stars): XML/SOAP for enterprise compatibility; heavy but sometimes required.

## Run the examples with uv
From the repo root:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install thriftpy2 jsonrpclib rpyc pyzmq msgpack pycapnp msgpack-rpc-python spyne zeep
```

- Use `uv run python <path>` to execute a server or client below.
- Cap'n Proto requires the `capnp` compiler on your PATH (e.g., `brew install capnp`).

---

## Apache Thrift (thriftpy2)
**Protocol:** IDL + binary/compact transports.

**Strengths:** Efficient, polyglot, stable governance.
**Weaknesses:** Schema step required; HTTP-native tooling is thinner than gRPC/REST.

Files: `examples/thrift/calculator.thrift`, `examples/thrift/server.py`, `examples/thrift/client.py`

`examples/thrift/server.py`
```python
import thriftpy2
from thriftpy2.rpc import make_server

calculator_thrift = thriftpy2.load("calculator.thrift", module_name="calculator_thrift")

class CalculatorHandler:
    def add(self, a, b):
        return a + b

server = make_server(calculator_thrift.Calculator, CalculatorHandler(), "0.0.0.0", 9090)
server.serve()
```

Run: `uv run python examples/thrift/server.py` and in another shell `uv run python examples/thrift/client.py`

---

## JSON-RPC (jsonrpclib)
**Protocol:** JSON-RPC 2.0 over HTTP or TCP.

**Strengths:** Human-readable, minimal setup.
**Weaknesses:** No schema enforcement; ad-hoc error contracts.

Files: `examples/jsonrpc/server.py`, `examples/jsonrpc/client.py`

`examples/jsonrpc/server.py`
```python
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

def add(a, b):
    return a + b

server = SimpleJSONRPCServer(("0.0.0.0", 4000))
server.register_function(add)
server.serve_forever()
```

Run: `uv run python examples/jsonrpc/server.py` and `uv run python examples/jsonrpc/client.py`

---

## RPyC
**Protocol:** Python-to-Python remote objects over TCP.

**Strengths:** Low ceremony for scripting/control channels; bidirectional callbacks available.
**Weaknesses:** Python-only; security sensitive if exposed broadly.

Files: `examples/rpyc/server.py`, `examples/rpyc/client.py`

`examples/rpyc/server.py`
```python
import rpyc
from rpyc.utils.server import ThreadedServer

class CalculatorService(rpyc.Service):
    def exposed_add(self, a, b):
        return a + b

server = ThreadedServer(CalculatorService, port=18861, protocol_config={"allow_public_attrs": True})
server.start()
```

Run: `uv run python examples/rpyc/server.py` and `uv run python examples/rpyc/client.py`

---

## ZeroMQ REQ/REP with msgpack
**Protocol:** Raw message passing with your own contract and msgpack payloads.

**Strengths:** High throughput, flexible socket patterns.
**Weaknesses:** You own serialization, versioning, and auth semantics.

Files: `examples/zeromq_msgpack/server.py`, `examples/zeromq_msgpack/client.py`

`examples/zeromq_msgpack/server.py`
```python
import msgpack
import zmq

ctx = zmq.Context()
sock = ctx.socket(zmq.REP)
sock.bind("tcp://*:5555")

while True:
    req = msgpack.loads(sock.recv(), raw=False)
    if req.get("method") == "add":
        a, b = req.get("params", [0, 0])
        sock.send(msgpack.dumps({"result": a + b}))
    else:
        sock.send(msgpack.dumps({"error": "unknown method"}))
```

Run: `uv run python examples/zeromq_msgpack/server.py` and `uv run python examples/zeromq_msgpack/client.py`

---

## Cap'n Proto (pycapnp)
**Protocol:** Schema-first, capability-oriented RPC with fast binary encoding.

**Strengths:** Extremely fast; schema evolution built in.
**Weaknesses:** Python binding is thinner; requires `capnp` compiler.

Files: `examples/capnp/calculator.capnp`, `examples/capnp/server.py`, `examples/capnp/client.py`

`examples/capnp/server.py`
```python
import capnp

calculator_capnp = capnp.load("calculator.capnp")

class Calculator(calculator_capnp.Calculator.Server):
    def add(self, a, b, _context, **_kwargs):
        return a + b

server = capnp.TwoPartyServer(("localhost", 7000), bootstrap=Calculator())
server.listen()
```

`examples/capnp/client.py`
```python
import capnp

calculator_capnp = capnp.load("calculator.capnp")

client = capnp.TwoPartyClient(("localhost", 7000))
calc = client.bootstrap().cast_as(calculator_capnp.Calculator)
resp = calc.add(2, 5).wait()
print("2 + 5 =", resp.result)
```

Run: `uv run python examples/capnp/server.py` and `uv run python examples/capnp/client.py`

---

## Msgpack-RPC (msgpack-rpc-python)
**Protocol:** JSON-RPC-like framing with msgpack payloads.

**Strengths:** Lightweight binary messages.
**Weaknesses:** Stale project (last push 2021); fewer contributors.

Files: `examples/msgpackrpc/server.py`, `examples/msgpackrpc/client.py`

`examples/msgpackrpc/server.py`
```python
from msgpackrpc import Address, Server

def add(a, b):
    return a + b

server = Server({"add": add})
server.listen(Address("0.0.0.0", 7001))
server.start()
```

Run: `uv run python examples/msgpackrpc/server.py` and `uv run python examples/msgpackrpc/client.py`

---

## SOAP (Spyne service + Zeep client)
**Protocol:** SOAP 1.1/1.2 over HTTP with WSDL.

**Strengths:** Enterprise interoperability; WSDL contracts.
**Weaknesses:** Verbose XML; heavier dependencies; fewer greenfield users.

Files: `examples/soap/service.py`, `examples/soap/client.py`

`examples/soap/service.py`
```python
from spyne import Application, ServiceBase, rpc, Integer
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

class Calculator(ServiceBase):
    @rpc(Integer, Integer, _returns=Integer)
    def add(ctx, a, b):
        return a + b

app = Application([Calculator], "calc.soap", in_protocol=Soap11(), out_protocol=Soap11())
wsgi_app = WsgiApplication(app)
server = make_server("0.0.0.0", 8000, wsgi_app)
server.serve_forever()
```

Run: `uv run python examples/soap/service.py` and `uv run python examples/soap/client.py`

---

## Top three alternatives to REST/gRPC (opinionated)
1) **Apache Thrift** – broad language coverage, efficient binary protocols, active project. Fits microservices needing schema and performance without gRPC.
2) **JSON-RPC (jsonrpclib)** – minimal setup, great for lightweight HTTP APIs, easy to interop and debug.
3) **RPyC** – best for Python-to-Python control planes and admin tasks where sharing objects is valuable.

## Notes on selection criteria
- Considered protocol diversity (schema-first vs message-passing vs dynamic), operational maturity, and visible repo activity.
- Excluded REST and gRPC by request; GraphQL omitted because it is query-centric rather than RPC.
- Activity data pulled via GitHub API with SSL verification disabled (local CA issue); timestamps reflect host clock (2025-11-20).
