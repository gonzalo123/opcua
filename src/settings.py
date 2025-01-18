import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')

load_dotenv(dotenv_path=BASE_DIR / 'env' / ENVIRONMENT / '.env')

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)

OPC_ENDPOINT = os.getenv('OPC_ENDPOINT')
OPC_NAMESPACE = os.getenv('OPC_NAMESPACE')
OPC_USERNAME = os.getenv('OPC_USERNAME')
OPC_PASSWORD = os.getenv('OPC_PASSWORD')

OPC_USERS_DB = {
    OPC_USERNAME: OPC_PASSWORD
}

CERT_DIR = BASE_DIR / 'cert'

OPC_CERTIFICATE = CERT_DIR / 'certificate.pem'
OPC_PRIVATE_KEY = CERT_DIR / 'private_key.pem'
