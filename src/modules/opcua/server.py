import asyncio
import base64
import logging

import redis.asyncio as redis
from asyncua import Server, ua
from asyncua.server.users import UserRole, User
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from settings import REDIS_PORT, REDIS_HOST, OPC_ENDPOINT, OPC_NAMESPACE, OPC_USERS_DB, OPC_CERTIFICATE, OPC_PRIVATE_KEY

logger = logging.getLogger(__name__)


class UserManager:
    def __init__(self, certificate_path, private_key_path):
        self.certificate = self.load_certificate(certificate_path)
        self.private_key = self.load_private_key(private_key_path)

    def load_certificate(self, cert_path):
        with open(cert_path, "rb") as cert_file:
            cert_data = cert_file.read()
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        return cert

    def load_private_key(self, key_path):
        with open(key_path, "rb") as key_file:
            key_data = key_file.read()
        private_key = serialization.load_pem_private_key(key_data, password=None, backend=default_backend())
        return private_key

    def validate_certificate(self, cert, private_key):
        public_key = cert.public_key()
        if isinstance(public_key, rsa.RSAPublicKey):
            private_numbers = private_key.private_numbers()
            public_numbers = public_key.public_numbers()
            if private_numbers.public_numbers == public_numbers:
                return True
            else:
                logger.error("Certificate public key does not match private key.")
        else:
            logger.error("The public key in the certificate is not an RSA key.")
        return False

    def get_user(self, iserver, username=None, password=None, certificate=None):
        if certificate:
            try:
                certificate_pem = base64.b64encode(certificate).decode('utf-8')
                certificate_pem = f"-----BEGIN CERTIFICATE-----\n{certificate_pem}\n-----END CERTIFICATE-----\n"
                cert = x509.load_pem_x509_certificate(certificate_pem.encode('utf-8'), default_backend())

                if self.validate_certificate(cert, self.private_key) and OPC_USERS_DB.get(username, False) == password:
                    logger.info(f"User '{username}' authenticated")
                    return User(role=UserRole.User)
            except ValueError as e:
                logger.error(f"Error loading certificate: {e}")
        return None


async def main():
    server = Server(user_manager=UserManager(OPC_CERTIFICATE, OPC_PRIVATE_KEY))
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
    asyncio.run(main(), debug=debug)
