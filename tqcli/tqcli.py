from tqcli.config.config import TQ_API_ROOT_URL, LOG_PATH
from tqcli.batch.server_handler import TranQuant

import optparse
import logging
import os

logger = logging.getLogger(os.path.basename(__file__))


def main():
    usage = '''

    ```
    $ tqcli --datasource-id <datasource-id> --input <dataset.file>
    ```
    '''

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
        default='66db6f2b-2da0-45c0-9ac5-08e9fb83eda5',
        help='Authentication token.',
    )

    parser.add_option(
        "-d", "--datasource-id",
        dest='datasource_id',
        default='',
        help='Data Source ID.',
    )

    parser.add_option(
        "-s", "--dataset-id",
        dest='dataset_id',
        default='',
        help='Data Set ID.',
    )

    options, remainder = parser.parse_args()

    tq = TranQuant(
        root_url=TQ_API_ROOT_URL,
        token=options.token,
        datasource_id=options.datasource_id,
        dataset_id=options.dataset_id
    )
    try:
        tq.is_valid()
        tq.upload(input_path=options.input_path)
    except Exception as ex:
        logger.info(ex)
        print('-'*50, '\n\n')
        print('TQCLI - For debugging please take a look at %s' % LOG_PATH)
        print('\n')
        print('With your feedback we will become more friendly! tell us what to do -> info@tranquant.com \n\t ~ Your friends at TranQuant.')
        print('\n\n', '-' * 50)

if __name__ == '__main__':
    main()
