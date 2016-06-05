import logging
import requests
import ujson

from batch.file_manager import TQFile
from config.config import DEFAULT_CHUNK_SIZE

LOGGER = logging.getLogger(__name__)


class Client(object):
    def __init__(self, destination_url, token, datasource_id):
        self.destination_url = destination_url
        self.datasource_id = datasource_id
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({'Token': token})

    def upload_file(self, tq_file):
        for from_byte, to_byte, remained_bytes, a_chunk in tq_file.chunks():
            payload = {
                'chunk': a_chunk,
                'from_byte': from_byte,
                'to_byte': to_byte,
                'remained_bytes': remained_bytes,
                'datasource_id': self.datasource_id
            }
            self.session.post(self.destination_url, data=ujson.dumps(payload))

    def close(self):
        self.session.close()


class TranQuant(object):
    def __init__(self, destination_url, token, datasource_id):
        self.client = Client(destination_url, token, datasource_id)

    def upload(self, input_path):
        tq_file = TQFile(input_path, chunk_size=DEFAULT_CHUNK_SIZE)
        if not tq_file.is_valid():
            raise Exception("The file is not valid.")
        self.client.upload_file(tq_file)

