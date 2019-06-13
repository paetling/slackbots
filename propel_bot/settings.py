import os

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
USE_REDIS = os.environ.get('USE_REDIS', False)
