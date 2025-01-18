import asyncio
import logging

from asyncua import Client

from settings import OPC_ENDPOINT, OPC_CERTIFICATE, OPC_PRIVATE_KEY

logger = logging.getLogger(__name__)


async def main():
    c = Client(url=OPC_ENDPOINT)
    await c.set_security_string(f"Basic256Sha256,SignAndEncrypt,{OPC_CERTIFICATE},{OPC_PRIVATE_KEY}")

    async with c:
        node = c.get_node("ns=2;i=2")
        value = await node.read_value()
        logger.info(f"Value: {value}")


def client(debug: bool = False):
    asyncio.run(main(), debug=debug)
