import logging
import os

#TQ_API_ROOT_URL = 'http://127.0.1.1:8090/dataset'
TQ_API_ROOT_URL = 'http://elb-tranquant-ecs-cluster-tqapi-1919110681.us-west-2.elb.amazonaws.com/dataset'
log_path = '/var/log/tqcli.log'

# the chunk size must be at least 5MB for multipart upload
DEFAULT_CHUNK_SIZE = 1024 * 1024 * 5 # 5MB

logger = logging.getLogger('tqcli')
fh = logging.FileHandler(log_path)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.addHandler(ch)