# Research Notes

- Initialized project folder and set up notes.
- Set research scope: Python RPC alternatives (JSON-RPC, Apache Thrift, RPyC, ZeroMQ, Cap'n Proto, Msgpack-RPC, SOAP).
- Collected GitHub activity via HTTPS with disabled SSL verification (system clock 2025):
  - Thrift (apache/thrift): stars 10835, last push 2025-11-19.
  - RPyC (tomerfiliba-org/rpyc): stars 1679, last push 2025-08-14.
  - jsonrpclib (tcalmant/jsonrpclib): stars 55, last push 2025-11-09.
  - PyZMQ (zeromq/pyzmq): stars 4032, last push 2025-11-17.
  - pycapnp (capnproto/pycapnp): stars 519, last push 2025-10-23.
  - msgpack-rpc-python: stars 212, last push 2021-11-27 (stale).
  - Zeep (SOAP): stars 1967, last push 2025-09-15.
- Selected candidates to cover protocol diversity: Thrift (IDL, binary), JSON-RPC over HTTP, RPyC (code execution binding), ZeroMQ REQ/REP with msgpack, Cap'n Proto (schema, zero-copy), Msgpack-RPC (lightweight RPC with msgpack, project stale), SOAP via Spyne/Zeep (enterprise legacy).
- Plan to include minimal server/client snippets for each to illustrate ergonomics and calling patterns without pulling upstream code.
- Drafted README with quick comparison, strengths/weaknesses, and minimal server/client snippets for each library (Thrift, jsonrpclib, RPyC, ZeroMQ+msgpack, Cap'n Proto, Msgpack-RPC, SOAP via Spyne/Zeep).
- Highlighted top 3 picks: Thrift, JSON-RPC, RPyC based on schema/efficiency, simplicity, and Python-centric remoting.
- Added runnable code examples (server/client) for each library under examples/, keeping payloads consistent (add two numbers).
- Swapped Thrift example to thriftpy2 to avoid codegen; added capnp, msgpack-rpc, SOAP, ZeroMQ+msgpack, JSON-RPC, and RPyC scripts.
- Updated README to include uv-based setup (`uv venv`, `uv pip install ...`) and commands to run each example via `uv run`.
