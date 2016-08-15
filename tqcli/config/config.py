import logging
from os.path import expanduser

#TQ_API_ROOT_URL = 'http://127.0.1.1:8090/dataset'
TQ_API_ROOT_URL = 'http://elb-tranquant-ecs-cluster-tqapi-1919110681.us-west-2.elb.amazonaws.com/dataset'
LOG_PATH = expanduser('~/tqcli.log')

# the chunk size must be at least 5MB for multipart upload
DEFAULT_CHUNK_SIZE = 1024 * 1024 * 5 # 5MB


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_PATH,
    filemode='w'
)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)


