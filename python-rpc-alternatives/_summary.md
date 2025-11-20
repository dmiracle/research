Exploring practical Python RPC alternatives to REST and gRPC, this comparison emphasizes schema-driven, message-oriented, and dynamic approaches suited for modern Python environments. Key contenders include **Apache Thrift** (active, schema-first), **JSON-RPC** (lightweight, HTTP-native), and **RPyC** (Python-to-Python object remoting), with additional coverage of ZeroMQ (custom sockets), Cap'n Proto (zero-copy binary), Msgpack-RPC (binary, but stale), and SOAP (enterprise/legacy). Each tool is reviewed for strengths, weaknesses, recency of development, and ease of deployment, with runnable examples using [`uv`](https://github.com/astral-sh/uv) for environment management. For broader language coverage and high efficiency, [Apache Thrift](https://github.com/apache/thrift) stands out, while JSON-RPC and RPyC excel in lightweight or pure Python scenarios.

**Key findings:**
- Thrift and Cap'n Proto offer schema-first, polyglot RPC, suitable for scalable microservices.
- JSON-RPC provides frictionless HTTP APIs but lacks schema enforcement.
- RPyC facilitates seamless Python control channels, ideal for automation but not secure for public services.
- ZeroMQ and Cap'n Proto excel in performance, but require custom contract management.
- SOAP still serves in enterprise contexts requiring WSDL contracts despite verbosity.
- Msgpack-RPC has low activity and less community support compared to other options.
