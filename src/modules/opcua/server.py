import asyncio
import logging

import redis.asyncio as redis
from asyncua import Server, ua
from asyncua.server.users import UserRole, User

from settings import REDIS_PORT, REDIS_HOST, OPC_ENDPOINT, OPC_NAMESPACE, OPC_USERS_DB, OPC_CERTIFICATE, OPC_PRIVATE_KEY

logger = logging.getLogger(__name__)


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
