import optparse
import os

from config.paths import TQ_DATASOURCE_UPLOAD_ENDPOINT
from tqhandler import TranQuant

if __name__ == '__main__':
    usage = """
    """
    parser = optparse.OptionParser(usage)
    parser.add_option(
        '-i', '--input',
        dest='input_path',
        default='',
        help='Path to the input file(s).',
    )

    parser.add_option(
        "-t", "--token",
        dest='token',
        default='',
        help='Authentication token.',
    )

    parser.add_option(
        "-d", "--datasource-id",
        dest='datasource_id',
        default='',
        help='DataSource ID.',
    )

    options, remainder = parser.parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))

    tq = TranQuant(destination_url=TQ_DATASOURCE_UPLOAD_ENDPOINT, token=options.token, datasource_id=options.datasource_id)
    tq.upload(input_path=options.input_path)















