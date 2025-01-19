import asyncio
import logging

from asyncua import Client, Node, ua

from settings import OPC_ENDPOINT, OPC_CERTIFICATE, OPC_PRIVATE_KEY, OPC_USERNAME, OPC_PASSWORD

logger = logging.getLogger(__name__)

async def browse_nodes(node: Node):
    node_class = await node.read_node_class()
    children = []
    for child in await node.get_children():
        if await child.read_node_class() in [ua.NodeClass.Object, ua.NodeClass.Variable]:
            children.append(await browse_nodes(child))
    if node_class != ua.NodeClass.Variable:
        var_type = None
    else:
        try:
            var_type = (await node.read_data_type_as_variant_type()).value
        except ua.UaError:
            logger.warning("Node Variable Type could not be determined for %r", node)
            var_type = None
    return {
        "id": node.nodeid.to_string(),
        "name": (await node.read_display_name()).Text,
        "cls": node_class.value,
        "children": children,
        "type": var_type,
    }

async def main():
    c = Client(url=OPC_ENDPOINT)
    c.set_user(OPC_USERNAME)
    c.set_password(OPC_PASSWORD)
    await c.set_security_string(f"Basic256Sha256,SignAndEncrypt,{OPC_CERTIFICATE},{OPC_PRIVATE_KEY}")

    async with c:
        tree = await browse_nodes(c.nodes.objects)
        logger.info("Node tree: %r", tree)

        node = c.get_node("ns=2;i=2")
        value = await node.read_value()
        logger.info(f"Value: {value}")


def client(debug: bool = False):
    asyncio.run(main(), debug=debug)
