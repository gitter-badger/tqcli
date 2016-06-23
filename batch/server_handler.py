import logging
import requests
import ujson
import base64

from batch.file_manager import TQFile
from config.config import DEFAULT_CHUNK_SIZE

LOGGER = logging.getLogger(__name__)


class Client(object):
    endpoints = {
        'datasource': '/ingest/datasource/upload/',
        'initiate': '/ingest/datasource/multipart/initiate/',
        'part': '/ingest/datasource/multipart/part/',
        'complete': '/ingest/datasource/multipart/complete/',
    }

    def __init__(self, root_url, token, datasource_id, dataset_id):
        self.root_url = root_url
        self.datasource_id = datasource_id
        self.dataset_id = dataset_id
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({'Token': token, 'Content-Type': 'application/json'})

    def initiate_multipart_upload(self):
        url = self.root_url + Client.endpoints['initiate']
        payload = {
            'datasource_id': self.datasource_id,
            'dataset_id': self.dataset_id
        }
        response = self.session.post(url, data=ujson.dumps(payload))
        print(response.content)
        return response.content

    def upload_part(self, upload_id, part_size, part_number, part):
        url = self.root_url + Client.endpoints['part']
        payload = {
            'file': {
                'datasource_id': self.datasource_id,
                'dataset_id': self.dataset_id
            },
            'upload_id': upload_id,
            'part_number': part_number,
            'part_size': part_size,
            'base64_part': base64.b64encode(part)
        }
        print('upload_part part_number: %s, part_size: %s' % (payload['part_number'], payload['part_size']))
        response = self.session.post(url, data=ujson.dumps(payload))
        print(response.content)
        return ujson.loads(response.content)

    def upload_complete(self, upload_id, part_tags):
        url = self.root_url + Client.endpoints['complete']
        print('part_tags: %s' % (part_tags) )
        payload = {
            'file': {
                'datasource_id': self.datasource_id,
                'dataset_id': self.dataset_id
            },
            'upload_id': upload_id,
            'part_tags': part_tags
        }
        print('upload_complete payload %s' % (ujson.dumps(payload)))
        response = self.session.post(url, data=ujson.dumps(payload))
        print(response.content)

    def upload_file_in_parts(self, tq_file):
        upload_id = self.initiate_multipart_upload()
        part_tags = [self.upload_part(upload_id, bytes_to_be_read, chunk_iterator, a_chunk) 
            for chunk_iterator, bytes_to_be_read, from_byte, to_byte, remained_bytes, a_chunk in tq_file.chunks()]
        self.upload_complete(upload_id, part_tags)

    def close(self):
        self.session.close()


class TranQuant(object):
    def __init__(self, root_url, token, datasource_id, dataset_id):
        self.client = Client(root_url, token, datasource_id, dataset_id)

    def upload(self, input_path):
        tq_file = TQFile(input_path, chunk_size=DEFAULT_CHUNK_SIZE)
        if not tq_file.is_valid():
            raise Exception("The file is not valid.")
        self.client.upload_file_in_parts(tq_file)
        # if tq_file.size < DEFAULT_CHUNK_SIZE:
        #     self.client.upload_file(tq_file)
        # else:
        #     self.client.upload_file_in_parts(tq_file)