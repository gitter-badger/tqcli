import tzlocal
import mimetypes
import os
import stat
import sys
import errno
from datetime import datetime
from dateutil.tz import tzutc, PY3


class TQFile(object):
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

    def __init__(self, path, chunk_size):
        self.path = self.relative_path(path)
        self.size, self.update_time = self.get_file_stat(path)
        self.content_type = self.guess_content_type(path)
        self.file = open(self.path, "rb")
        self.chunk_size = chunk_size
        self.index = 0

    def is_valid(self):
        return all(
            [
                self.is_readable(self.path),
                not self.is_special_file(self.path)
            ]
        )

    def chunks(self):
        chunk_iterator = 0
        bytes_read = 0
        while bytes_read < self.size:
            chunk_iterator += 1
            from_byte = bytes_read
            bytes_to_be_read = min(self.size - bytes_read, self.chunk_size)
            a_chunk = self.file.read(bytes_to_be_read)
            bytes_read += bytes_to_be_read
            to_byte = bytes_read
            remained_bytes = self.size - bytes_read
            yield chunk_iterator, bytes_to_be_read, from_byte, to_byte, remained_bytes, a_chunk

    def is_readable(self, path):
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
                with open(path, 'r') as fd:
                    pass
            except (OSError, IOError):
                return False
        return True

    def is_special_file(self, path):
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

    def get_file_stat(self, path):
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
            update_time = datetime.fromtimestamp(stats.st_mtime, tzlocal.get_localzone())
        except ValueError:
            # Python's fromtimestamp raises value errors when the timestamp is out
            # of range of the platform's C localtime() function. This can cause
            # issues when syncing from systems with a wide range of valid timestamps
            # to systems with a lower range. Some systems support 64-bit timestamps,
            # for instance, while others only support 32-bit. We don't want to fail
            # in these cases, so instead we pass along none.
            update_time = None

        return stats.st_size, update_time

    def bytes_print(self, statement):
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

    def guess_content_type(self, filename):
        """Given a filename, guess it's content type.
        If the type cannot be guessed, a value of None is returned.
        """
        return mimetypes.guess_type(filename)[0]

    def relative_path(self, filename, start=os.path.curdir):
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

    def human_readable_to_bytes(self, value):
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
            len(value) >= 2 and suffix in TQFile.SIZE_SUFFIX)
        if not has_size_identifier:
            try:
                return int(value)
            except ValueError:
                raise ValueError("Invalid size value: %s" % value)
        else:
            multiplier = TQFile.SIZE_SUFFIX[suffix]
            return int(value[:-len(suffix)]) * multiplier

    def human_readable_size(self, value):
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

        for i, suffix in enumerate(TQFile.HUMANIZE_SUFFIXES):
            unit = base ** (i + 2)
            if round((bytes_int / unit) * base) < base:
                return '%.1f %s' % ((base * bytes_int / unit), suffix)

    def set_file_utime(self, filename, desired_time):
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
            raise Exception(
                ("The file was downloaded, but attempting to modify the "
                 "utime of the file failed. Is the file owned by another user?"))