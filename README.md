## Implementing Industrial OPC UA Communication with Python and Asyncio

Today we're going to work with an industrial protocol called OPC UA. We'll be using the [opcua-asyncio](https://github.com/FreeOpcUa/opcua-asyncio) library to create a simple OPC UA server and client. We'll also be using the `asyncio` library to handle the asynchronous communication between the server and the client. The idea es build a OPC UA server that exposes a variable and a client that reads and writes to that variable. 

To simulate a changing variable, I've created a simple script that changes one variable every second with the value of the current time and persists it to a Redis database.

```python
import logging
import time

import redis

from settings import REDIS_HOST, REDIS_PORT

logger = logging.getLogger(__name__)


def update_redis_variable_loop():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    while True:
        timestamp_ms = int(time.time() * 1_000)
        r.set('ts', timestamp_ms)
        logger.info(f"Updated variable: {timestamp_ms}")
        time.sleep(1)
```

The server will have an authentication mechanism using a username and password, and it will also have a self-signed certificate and a private key to encrypt the communication. To generate the self-signed certificate and private key, you can use the following commands:

```bash
openssl genpkey -algorithm RSA -out private_key.pem
openssl req -new -key private_key.pem -out certificate.csr
openssl x509 -req -days 365 -in certificate.csr -signkey private_key.pem -out certificate.pem
```

This OPC UA server will expose the variable that we're updating in the Redis database.

```python
class UserManager:
    def get_user(self, iserver, username=None, password=None, certificate=None):
        if certificate and OPC_USERS_DB.get(username, False) == password:
            logger.info(f"User '{username}' authenticated")
            return User(role=UserRole.User)
        return None


async def main():
    server = Server(user_manager=UserManager())
    await server.init()
    server.set_endpoint(OPC_ENDPOINT)

    await server.load_certificate(OPC_CERTIFICATE)
    await server.load_private_key(OPC_PRIVATE_KEY)
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])

    namespace_idx = await server.register_namespace(OPC_NAMESPACE)
    obj = await server.nodes.objects.add_object(namespace_idx, "Gonzalo")
    var = await obj.add_variable(namespace_idx, "T", 0, datatype=ua.VariantType.Int32)
    await var.set_writable(False)

    redis_client = await redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    logger.info(f"Starting server on {OPC_ENDPOINT}")

    async with server:
        while True:
            await asyncio.sleep(1)
            value = await redis_client.get('ts')
            if value is not None:
                value = int(value)
                logger.info(f"Set value of {var} to {value}")
                await var.write_value(value)


def server(debug: bool = False):
    if debug:
        asyncio.get_event_loop().set_debug(True)
    asyncio.run(main())
```

And now we create a OPC UA client that reads the variable from the server and prints it to the console.

```python
import asyncio
import logging

from asyncua import Client

from settings import OPC_ENDPOINT, OPC_CERTIFICATE, OPC_PRIVATE_KEY, OPC_USERNAME, OPC_PASSWORD

logger = logging.getLogger(__name__)


async def main():
    c = Client(url=OPC_ENDPOINT)
    c.set_user(OPC_USERNAME)
    c.set_password(OPC_PASSWORD)
    await c.set_security_string(f"Basic256Sha256,SignAndEncrypt,{OPC_CERTIFICATE},{OPC_PRIVATE_KEY}")

    async with c:
        node = c.get_node("ns=2;i=2")
        value = await node.read_value()
        logger.info(f"Value: {value}")


def client(debug: bool = False):
    asyncio.run(main(), debug=debug)
```