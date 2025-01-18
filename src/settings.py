from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

OPC_ENDPOINT = 'opc.tcp://0.0.0.0:4840/opcua'
OPC_NAMESPACE = 'https://gonzalo123.com/opcua'
OPC_USERNAME = 'username'
OPC_PASSWORD = 'password'

OPC_USERS_DB = {
    OPC_USERNAME: OPC_PASSWORD
}

CERT_DIR = BASE_DIR / 'cert'

OPC_CERTIFICATE = CERT_DIR / 'certificate.pem'
OPC_PRIVATE_KEY = CERT_DIR / 'private_key.pem'
