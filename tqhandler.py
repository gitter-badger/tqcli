import requests
from fileutils import is_readable, is_special_file, get_file_stat, guess_content_type, relative_path
from paths import TQ_DATASOURCE_META_ENDPOINT


class TQFile(object):
    def __init__(self, path):
        self.path = relative_path(path)
        self.size, self.update_time = get_file_stat(path)
        self.content_type = guess_content_type(path)
        self.file = open(self.path, "rb")

    def is_valid(self):
        return all(
            [
                is_readable(self.path),
                not is_special_file(self.path)
            ]
        )


class Client(object):
    def __init__(self, destination_url, token, datasource_id):
        self.destination_url = destination_url
        self.session = requests.Session()
        self.session.headers.update({
            'Token': token,
            'Dataource': datasource_id
        })

    def upload_file(self, f):
        self.session.post(self.destination_url, data=f)

    def close(self):
        self.session.close()


class TranQuant(object):
    def __init__(self, destination_url, token, datasource_id):
        self.client = Client(destination_url, token, datasource_id)

    def upload(self, _path):
        tq_file = TQFile(_path)
        if not tq_file.is_valid():
            raise Exception("The file is not valid.")
        self.client.upload_file(tq_file)

