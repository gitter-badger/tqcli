import logging
import requests
import ujson
import base64

from batch.file_manager import TQFile
from config.config import DEFAULT_CHUNK_SIZE

LOGGER = logging.getLogger(__name__)


class Client(object):
    endpoints = {
        'initiate': '/upload/initiate/',
        'part': '/upload/part/',
        'complete': '/upload/complete/'
    }

    def __init__(self, root_url, token, datasource_id, dataset_id):
        self.root_url = root_url
        self.datasource_id = datasource_id
        self.dataset_id = dataset_id
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'token token="%s"' % self.token, 'Content-Type': 'application/json'})

    def upload_file_in_parts(self, tq_file):
        filename = tq_file.filename()
        file_and_upload_id = self.initiate_multipart_upload(filename)
        upload_id = file_and_upload_id["upload_id"]
        self.dataset_id = file_and_upload_id['file']['dataset_id']
        part_tags = [self.upload_part(upload_id, bytes_to_be_read, chunk_iterator, a_chunk, filename, total_chunks) 
            for chunk_iterator, bytes_to_be_read, from_byte, to_byte, remained_bytes, a_chunk, total_chunks in tq_file.chunks()]
        self.upload_complete(upload_id, part_tags, filename)

    def initiate_multipart_upload(self, filename):
        url = self.root_url + Client.endpoints['initiate']
        payload = {
          'datasource_id': self.datasource_id,
          'filename': filename
        }
        response = self.session.post(url, data=ujson.dumps(payload))
        #print(response.content)
        #print(response.status_code)
        if response.status_code == 401:
            raise Exception("Authentication Failed.  Token is invalid.")
        print("Initiated upload")
        return ujson.loads(response.content)

    def upload_part(self, upload_id, part_size, part_number, part, filename, total_parts):
        url = self.root_url + Client.endpoints['part']
        payload = {
            'file': {
              'datasource_id': self.datasource_id,
              'dataset_id': self.dataset_id,
              'filename': filename
            },
            'upload_id': upload_id,
            'part_number': part_number,
            'part_size': part_size,
            'base64_part': base64.b64encode(part)
        }
        print("Uploading part %s of %s (%s bytes)" % (part_number, total_parts, part_size))
        #print('upload_part part_number: %s, part_size: %s' % (payload['part_number'], payload['part_size']))
        response = self.session.post(url, data=ujson.dumps(payload))
        #print(response.content)
        return ujson.loads(response.content)

    def upload_complete(self, upload_id, part_tags, filename):
        url = self.root_url + Client.endpoints['complete']
        #print('part_tags: %s' % (part_tags) )
        payload = {
            'file': {
                'datasource_id': self.datasource_id,
                'dataset_id': self.dataset_id,
                'filename': filename
            },
            'upload_id': upload_id,
            'part_tags': part_tags
        }
        #print('upload_complete payload %s' % (ujson.dumps(payload)))
        response = self.session.post(url, data=ujson.dumps(payload))
        #print(response.content)
        if response.status_code == 200:
            print("Upload complete!")

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