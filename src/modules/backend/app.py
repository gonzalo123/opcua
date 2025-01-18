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
