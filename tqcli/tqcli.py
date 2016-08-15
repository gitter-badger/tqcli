from tqcli.config.config import TQ_API_ROOT_URL, LOG_PATH
from tqcli.batch.server_handler import TranQuant

import optparse
import logging
import os

logger = logging.getLogger(os.path.basename(__file__))


def main():
    usage = '''

    ```
    $ tqcli --input <dataset.file> --token <user-token> --datasource-id <datasource-id>
    ```


    Example:

    ```
    $ tqcli --input data\all-shakespeare.txt --token SECRET_TOKEN --datasource-id 524b0f9f-d829-4ea7-8e62-e06d21b3dd13

        Initiated upload
        Uploading part 1 of 2 (5242880 bytes)
        Uploading part 2 of 2 (99881 bytes)
        Upload complete!


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
        default='',
        help='Authentication token.',
    )

    parser.add_option(
        "-d", "--datasource-id",
        dest='datasource_id',
        default='',
        help='DataSource ID.',
    )

    parser.add_option(
        "-s", "--dataset-id",
        dest='dataset_id',
        default='',
        help='DataSet ID.',
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
        print('Help us become more friendly with your feedback :)!  -> info@tranquant.com \n\t ~ Your friends at TranQuant.')
        print('\n\n', '-' * 50)

if __name__ == '__main__':
    main()
