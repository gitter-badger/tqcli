import logging
import mimetypes
import os
import sys
import stat
from datetime import datetime

import errno
from dateutil.tz import tzlocal, tzutc, PY3
from dateutil.parser import parse

import tzlocal as tzlocal

_open = open

LOGGER = logging.getLogger(__name__)
HUMANIZE_SUFFIXES = ('KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB')
MAX_PARTS = 10000
EPOCH_TIME = datetime(1970, 1, 1, tzinfo=tzutc())
# The maximum file size you can upload via S3 per request.
# See: http://docs.aws.amazon.com/AmazonS3/latest/dev/UploadingObjects.html
# and: http://docs.aws.amazon.com/AmazonS3/latest/dev/qfacts.html
MAX_SINGLE_UPLOAD_SIZE = 5 * (1024 ** 3)
MIN_UPLOAD_CHUNKSIZE = 5 * (1024 ** 2)
# Maximum object size allowed in S3.
# See: http://docs.aws.amazon.com/AmazonS3/latest/dev/qfacts.html
MAX_UPLOAD_SIZE = 5 * (1024 ** 4)
SIZE_SUFFIX = {
    'kb': 1024,
    'mb': 1024 ** 2,
    'gb': 1024 ** 3,
    'tb': 1024 ** 4,
    'kib': 1024,
    'mib': 1024 ** 2,
    'gib': 1024 ** 3,
    'tib': 1024 ** 4,
}


def human_readable_size(value):
    """Convert an size in bytes into a human readable format.
    For example::
        >>> human_readable_size(1)
        '1 Byte'
        >>> human_readable_size(10)
        '10 Bytes'
        >>> human_readable_size(1024)
        '1.0 KiB'
        >>> human_readable_size(1024 * 1024)
        '1.0 MiB'
    :param value: The size in bytes
    :return: The size in a human readable format based on base-2 units.
    """
    one_decimal_point = '%.1f'
    base = 1024
    bytes_int = float(value)

    if bytes_int == 1:
        return '1 Byte'
    elif bytes_int < base:
        return '%d Bytes' % bytes_int

    for i, suffix in enumerate(HUMANIZE_SUFFIXES):
        unit = base ** (i + 2)
        if round((bytes_int / unit) * base) < base:
            return '%.1f %s' % ((base * bytes_int / unit), suffix)


def human_readable_to_bytes(value):
    """Converts a human readable size to bytes.
    :param value: A string such as "10MB".  If a suffix is not included,
        then the value is assumed to be an integer representing the size
        in bytes.
    :returns: The converted value in bytes as an integer
    """
    value = value.lower()
    if value[-2:] == 'ib':
        # Assume IEC suffix.
        suffix = value[-3:].lower()
    else:
        suffix = value[-2:].lower()
    has_size_identifier = (
        len(value) >= 2 and suffix in SIZE_SUFFIX)
    if not has_size_identifier:
        try:
            return int(value)
        except ValueError:
            raise ValueError("Invalid size value: %s" % value)
    else:
        multiplier = SIZE_SUFFIX[suffix]
        return int(value[:-len(suffix)]) * multiplier


def is_special_file(path):
    """
    This function checks to see if a special file.  It checks if the
    file is a character special device, block special device, FIFO, or
    socket.
    """
    mode = os.stat(path).st_mode
    # Character special device.
    if stat.S_ISCHR(mode):
        return True
    # Block special device
    if stat.S_ISBLK(mode):
        return True
    # FIFO.
    if stat.S_ISFIFO(mode):
        return True
    # Socket.
    if stat.S_ISSOCK(mode):
        return True
    return False


def is_readable(path):
    """
    This function checks to see if a file or a directory can be read.
    This is tested by performing an operation that requires read access
    on the file or the directory.
    """
    if os.path.isdir(path):
        try:
            os.listdir(path)
        except (OSError, IOError):
            return False
    else:
        try:
            with _open(path, 'r') as fd:
                pass
        except (OSError, IOError):
            return False
    return True


def get_file_stat(path):
    """
    This is a helper function that given a local path return the size of
    the file in bytes and time of last modification.
    """
    try:
        stats = os.stat(path)
    except IOError as e:
        raise ValueError('Could not retrieve file stat of "%s": %s' % (
            path, e))

    try:
        update_time = datetime.fromtimestamp(stats.st_mtime, tzlocal())
    except ValueError:
        # Python's fromtimestamp raises value errors when the timestamp is out
        # of range of the platform's C localtime() function. This can cause
        # issues when syncing from systems with a wide range of valid timestamps
        # to systems with a lower range. Some systems support 64-bit timestamps,
        # for instance, while others only support 32-bit. We don't want to fail
        # in these cases, so instead we pass along none.
        update_time = None

    return stats.st_size, update_time

def bytes_print(statement):
    """
    This function is used to properly write bytes to standard out.
    """
    if PY3:
        if getattr(sys.stdout, 'buffer', None):
            sys.stdout.buffer.write(statement)
        else:
            # If it is not possible to write to the standard out buffer.
            # The next best option is to decode and write to standard out.
            sys.stdout.write(statement.decode('utf-8'))
    else:
        sys.stdout.write(statement)


def guess_content_type(filename):
    """Given a filename, guess it's content type.
    If the type cannot be guessed, a value of None is returned.
    """
    return mimetypes.guess_type(filename)[0]


def relative_path(filename, start=os.path.curdir):
    """Cross platform relative path of a filename.
    If no relative path can be calculated (i.e different
    drives on Windows), then instead of raising a ValueError,
    the absolute path is returned.
    """
    try:
        dirname, basename = os.path.split(filename)
        relative_dir = os.path.relpath(dirname, start)
        return os.path.join(relative_dir, basename)
    except ValueError:
        return os.path.abspath(filename)


def set_file_utime(filename, desired_time):
    """
    Set the utime of a file, and if it fails, raise a more explicit error.
    :param filename: the file to modify
    :param desired_time: the epoch timestamp to set for atime and mtime.
    :raises: SetFileUtimeError: if you do not have permission (errno 1)
    :raises: OSError: for all errors other than errno 1
    """
    try:
        os.utime(filename, (desired_time, desired_time))
    except OSError as e:
        # Only raise a more explicit exception when it is a permission issue.
        if e.errno != errno.EPERM:
            raise e
        raise SetFileUtimeError(
            ("The file was downloaded, but attempting to modify the "
             "utime of the file failed. Is the file owned by another user?"))


class SetFileUtimeError(Exception):
    pass


class ReadFileChunk(object):
    def __init__(self, filename, start_byte, size):
        self._filename = filename
        self._start_byte = start_byte
        self._fileobj = open(self._filename, 'rb')
        self._size = self._calculate_file_size(self._fileobj, requested_size=size,
                                               start_byte=start_byte)
        self._fileobj.seek(self._start_byte)
        self._amount_read = 0

    def _calculate_file_size(self, fileobj, requested_size, start_byte):
        actual_file_size = os.fstat(fileobj.fileno()).st_size
        max_chunk_size = actual_file_size - start_byte
        return min(max_chunk_size, requested_size)

    def read(self, amount=None):
        if amount is None:
            remaining = self._size - self._amount_read
            data = self._fileobj.read(remaining)
            self._amount_read += remaining
            return data
        else:
            actual_amount = min(self._size - self._amount_read, amount)
            data = self._fileobj.read(actual_amount)
            self._amount_read += actual_amount
            return data

    def seek(self, where):
        self._fileobj.seek(self._start_byte + where)
        self._amount_read = where

    def close(self):
        self._fileobj.close()

    def tell(self):
        return self._amount_read

    def __len__(self):
        # __len__ is defined because requests will try to determine the length
        # of the stream to set a content length.  In the normal case
        # of the file it will just stat the file, but we need to change that
        # behavior.  By providing a __len__, requests will use that instead
        # of stat'ing the file.
        return self._size

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._fileobj.close()

    def __iter__(self):
        # This is a workaround for http://bugs.python.org/issue17575
        # Basically httplib will try to iterate over the contents, even
        # if its a file like object.  This wasn't noticed because we've
        # already exhausted the stream so iterating over the file immediately
        # steps, which is what we're simulating here.
        return iter([])


def _date_parser(date_string):
    return parse(date_string).astimezone(tzlocal())
