import os
import ujson
import tornado.ioloop
import tornado.web

LOG_FILE_PATH = './tqserver.log'

class AnalyticsHandler(tornado.web.RequestHandler):
    def initialize(self, log_file):
        self.log_file = log_file

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, Token")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def post(self, *args, **kwargs):
        try:
            print('KWARGS: ', kwargs)
            data = dict()
            # data['ip'] = self.request.remote_ip
            # data['ua'] = self.request.headers.get('User-Agent')
            # data['uuid'] = self.request.headers['Token']

            content = tornado.escape.json_decode(self.request.body)
            data['chunk'] = content.get('chunk')
            data['from_byte'] = content.get('from_byte')
            data['to_byte'] = content.get('to_byte')
            data['remained_bytes'] = content.get('remained_bytes')
            data['datasource_id'] = content.get('datasource_id')
            print('CHUNK: ', data)
            # os.write(self.log_file, ujson.dumps(data) + '\n')
        except Exception as ex:
            print(ex)

    def options(self):
        self.set_status(204)
        self.finish()


def make_app():
    return tornado.web.Application([
        (r"/api/ingest/datasource/", AnalyticsHandler, dict(log_file=os.open(LOG_FILE_PATH, os.O_CREAT | os.O_WRONLY | os.O_NONBLOCK))),
    ])


if __name__ == "__main__":
    while True:
        try:
            app = make_app()
            app.listen(9999)
            tornado.ioloop.IOLoop.current().start()
        except Exception as ex:
            print(ex)