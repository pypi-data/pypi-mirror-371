from __future__ import annotations

import csv
import pathlib
import queue
import re
import threading
from collections import deque
from contextlib import AbstractContextManager
from datetime import datetime
from logging import getLogger
from typing import TYPE_CHECKING

from dateutil import tz

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Any, TextIO

    from eta_nexus.nodes import Node
    from eta_nexus.util.type_annotations import Number, Path, Self, TimeStep

from eta_nexus.subhandlers.subhandler import SubscriptionHandler

log = getLogger(__name__)


class CsvSubHandler(SubscriptionHandler):
    """Handle data for a subscription and save it as a CSV file.

    :param output_file: CSV file to write data to.
    :param write_interval: Interval between rows in the CSV file (value that time is rounded to)
    :param size_limit: Size limit for the csv file. A new file with a unique name will be created when the size
        is exceeded.
    :param dialect: Dialect of the csv file. This takes objects, which correspond to the csv.Dialect interface from the
        python csv module.
    """

    def __init__(
        self,
        output_file: Path,
        write_interval: TimeStep = 1,
        size_limit: int = 1024,
        dialect: type[csv.Dialect] = csv.excel,
    ) -> None:
        super().__init__(write_interval=write_interval)

        # Create the csv file handler object which writes data to disc
        self._csv_file = _CSVFileDB(output_file, size_limit, dialect)

        # Enable propagation of exceptions
        self.exc: BaseException | None = None

        # Create the queue and thread
        self._queue: queue.Queue = queue.Queue()
        self._thread: threading.Thread = threading.Thread(target=self._run)
        self._thread.start()

    def push(self, node: Node, value: Any, timestamp: datetime | None = None) -> None:
        """Receive data from a subscription. THis should contain the node that was requested, a value and a timestamp
        when data was received. If the timestamp is not provided, current time will be used.

        :param node: Node object the data belongs to.
        :param value: Value of the data.
        :param timestamp: Timestamp of receiving the data.
        """
        timestamp = timestamp if timestamp is not None else datetime.now()
        self._queue.put_nowait((node, value, timestamp))

        # Reraise exceptions if any
        if self.exc:
            raise self.exc

    def _run(self) -> None:
        """Take data from the queue, preprocess it and write to output file."""
        cancelled = False

        with self._csv_file as f:
            try:
                while True:
                    try:
                        data = self._queue.get_nowait()
                    except queue.Empty:
                        if not cancelled:
                            continue

                    # Check for sentinel and finalize thread after completing open tasks
                    if data is None:
                        self._queue.task_done()
                        cancelled = True
                        continue
                    if cancelled is True and self._queue.empty():
                        break

                    node, value, timestamp = data

                    # Make sure not to send lists to the file handler
                    if not isinstance(value, str) and hasattr(value, "__len__"):
                        value = self._format_list(value)
                    if hasattr(timestamp, "__len__"):
                        timestamp = timestamp[0]
                    timestamp = self._round_timestamp(timestamp).astimezone(self._local_tz)

                    f.write(timestamp, node.name, value)
                    self._queue.task_done()
            except Exception as e:
                self.exc = e

    def close(self) -> None:
        """Finalize and close the subscription handler."""
        # Reraise exceptions if any
        if self.exc:
            raise self.exc

        self._queue.put_nowait(None)
        self._queue.join()
        self._thread.join()

    def _format_list(self, value: Any) -> str:
        delim = ";" if self._csv_file.dialect.delimiter == "," else ","
        return repr(value).replace(self._csv_file.dialect.delimiter, delim)


class _CSVFileDB(AbstractContextManager):
    """Handle CSV file content.

    :param file: Path to the csv file.
    :param file_size_limit: Size limit for the file in MB. A new file will be created, once the limit is exceeded.
    :param dialect: Dialect of the csv file. This takes objects, which correspond to the csv.Dialect interface from the
        python csv module.
    """

    def __init__(
        self,
        file: Path,
        file_size_limit: int = 1024,
        dialect: type[csv.Dialect] = csv.excel,
    ) -> None:
        #: Path to the file that is being written to.
        self.filepath: pathlib.Path = file if isinstance(file, pathlib.Path) else pathlib.Path(file)
        #: File descriptor.
        self._file: TextIO
        #: Size limit for written files in bytes.
        self.file_size_limit: int = file_size_limit * 1024 * 1024
        #: CSV dialect to be used for reading and writing data.
        self.dialect: type[csv.Dialect] = dialect

        #: List of header fields.
        self._header: list[str] = []
        #: Ending position of the header in the file stream (used for extending the header).
        self._endof_header: int = 0
        #: Write buffer.
        self._buffer: deque[dict[str, str]] = deque()
        self._timebuffer: deque[datetime] = deque()
        #: Latest timestamp in the write-buffer.
        self._latest_ts: datetime = datetime.fromtimestamp(10000, tz=tz.tzlocal())
        #: Latest known value for each of the names in the header.
        self._latest_values: dict[str, str] = {}
        #: Length of the line terminator in bytes (for finding file positions).
        self._len_lineterminator: int = len(bytes(self.dialect.lineterminator, "UTF-8"))

        self._file = self._check_file(filepath=self.filepath, exclusive_creation=False)
        self._check_valid_csv()

    def __enter__(self) -> Self:
        """Enter the context managed file database."""
        self._open_file()
        return self

    def _open_file(self, *, exclusive_creation: bool = False) -> None:
        """Open a new file and check whether it is writable. If the file exists, try to figure out the dialect and
        header of the existing file.

        :param exclusive_creation: Set to True, to request exclusive creation of a new file. If set to False, an
            existing file may be updated.
        """
        self._file = self._check_file(filepath=self.filepath, exclusive_creation=exclusive_creation)
        self._check_valid_csv()

        # Go to the end to get ready for updating/extending the file.
        self._file.seek(0, 2)

    def _check_valid_csv(self) -> None:
        """Check whether the file is a valid csv file."""
        # If the file is not empty, go to the beginning and try to figure out, whether existing data could be extended.
        if self._file.readline() in "":
            valid = True
            self._header = ["Timestamp"]
            self._write_file(self._header)
            self._endof_header = self._file.tell() - self._len_lineterminator
            log.debug(f"The '.csv' file was empty, dialect set to {self.dialect}, started writing header.")
        else:
            self._file.seek(0)

            # Read a maximum of 30 lines from the file to use as a sample for figuring out, whether the file
            # is valid csv
            sample_lines = []
            for _ in range(30):
                sample_lines.append(self._file.readline())

                if sample_lines[-1] == "":
                    break

            sample = "".join(sample_lines)
            try:
                valid = csv.Sniffer().has_header(sample)
                self.dialect = csv.Sniffer().sniff(sample)
                self.dialect.delimiter = "," if self.dialect.delimiter not in {",", ";"} else self.dialect.delimiter
                self._len_lineterminator = len(bytes(self.dialect.lineterminator, "UTF-8"))
            except csv.Error:
                valid = False
                self.dialect = csv.excel

            # Determine the header of the existing csv file
            self._file.seek(0)
            self._header = list(re.sub(r"\s+", "", self._file.readline()).split(self.dialect.delimiter))
            self._endof_header = self._file.tell() - self._len_lineterminator
        if not valid:
            raise ValueError(f"Output file for writing to '.csv' is not a valid '.csv' file: {self.filepath}.")

    @staticmethod
    def _check_file(filepath: pathlib.Path, *, exclusive_creation: bool = False) -> TextIO:
        # Try opening or creating the specified file.
        try:
            if exclusive_creation:
                raise FileNotFoundError  # noqa: TRY301

            file = filepath.open("r+t", newline="", encoding="UTF-8")
        except FileNotFoundError:
            try:
                file = filepath.open("x+t", newline="", encoding="UTF-8")
                log.debug(f"Created a new '.csv' file: {filepath}.")
            except OSError as e:
                raise OSError(f"Unable to read or write the requested '.csv' file: {filepath}.") from e
        else:
            log.debug(f"Opened existing '.csv' file for updating: {filepath}.")
        # Check whether the file is accessible in the required ways.
        if file is None or not file.readable() or not file.seekable() or not file.writable():
            raise ValueError("Output file for writing to '.csv' is not readable or writable.")
        log.debug("Successfully verified full '.csv' file access")
        return file

    def _write_file(self, field_list: list[str], insert_pos: int | None = None) -> int:
        """Write data to the file.

        :param field_list: List of strings to be inserted into the csv file.
        :param insert_pos: Position to insert the fields (stream position). If None, insertion will be at end of file.
        :return: Ending position of the last insertion (stream position).
        """
        # Check whether the file is accessible in the required ways.
        if self._file is None or not self._file.readable() or not self._file.seekable() or not self._file.writable():
            raise ValueError("Output file for writing to '.csv' is not readable or writable.")

        if insert_pos is None:
            string = self.dialect.delimiter.join(field_list) + self.dialect.lineterminator

            try:
                self._file.write(string)
            except ValueError:
                self._open_file()
                self._file.write(string)

            pos = self._file.tell()
        else:
            # When inserting, everything else in the file must be moved along as well
            # (otherwise it would be overwritten). Therefore, a chunk of the file is read before inserting
            string = self.dialect.delimiter + self.dialect.delimiter.join(field_list)
            chunksize = max(100000, len(string))

            self._file.seek(insert_pos)
            chunk = self._file.read(chunksize)
            nextpos_read = self._file.tell()
            self._file.seek(insert_pos)
            self._file.write(string)
            pos = nextpos_insert = self._file.tell()

            while nextpos_insert < nextpos_read:
                self._file.seek(nextpos_read)
                newchunk = self._file.read(chunksize)
                nextpos_read = self._file.tell()
                # Insert last chunk into file and store next chunk
                self._file.seek(nextpos_insert)
                self._file.write(chunk)

                # Store current position for next insertion, then read next chunk
                nextpos_insert = self._file.tell()
                chunk = newchunk
            self._file.seek(nextpos_insert)
            self._file.write(chunk)

        return pos

    def write(
        self,
        timestamp: datetime | None = None,
        name: str | None = None,
        value: Number | None = None,
        *,
        flush: bool = False,
        _len_buffer: int = 20,
    ) -> None:
        """Write value to the file and manage the data buffer.

        :param timestamp: Timestamp of the value to be written (can be empty if only flushing the buffer is intended).
        :param name: Name/Header for the value to be written (can be empty if only flushing the buffer is intended).
        :param value: Value to be written to the file (can be empty if only flushing the buffer is intended).
        :param flush: Flush the entire buffer to file if set to True.
        :param _len_buffer: Length of the buffer in lines. Does not usually need to be changed.
        """
        if self._file is None:
            raise RuntimeError("Enter context manager before trying to write to CSVFileDB.")

        # Check whether the file size limit is exceeded to initiate switching to a new file.
        size_limit_exceeded = self.filepath.stat().st_size > self.file_size_limit

        # Determine how large the buffer should be, depending on whether data is being flushed to file or preparing to
        # switch to a new file.
        if flush:
            buffer_target = 0
        elif size_limit_exceeded and not len(self._buffer) >= 2 * _len_buffer:
            buffer_target = 2 * _len_buffer
            log.debug("Preparing to switch files due to exceeded CSV file size limit.")
        else:
            buffer_target = _len_buffer

        # New values are inserted into the buffer, depending on their timestamp
        if timestamp is not None and name is not None and value is not None:
            # Extend header, if the value does not exist there yet
            if name not in self._header:
                self._header.append(name)
                self._endof_header = self._write_file([name], self._endof_header)

            # Find out, where to insert the current timestamp
            if len(self._timebuffer) == 0 or self._timebuffer[-1] < timestamp:
                # If the new timestamp occurred later than the latest timestamp
                self._buffer.append({name: str(value)})
                self._timebuffer.append(timestamp)
            elif self._timebuffer[-1] == timestamp:
                # If the timestamp is equal to the latest timestamp
                self._buffer[-1].update({name: str(value)})
            elif self._timebuffer[0] > timestamp:
                # If the new timestamp occurred before the earliest buffered timestamp
                self._buffer.appendleft({name: str(value)})
                self._timebuffer.appendleft(timestamp)
                log.debug(f"Buffer time for CSV file exceeded, older value received with {timestamp}")
            else:
                # If none of the special cases above apply, search through the time buffer to figure out, where to
                # insert the value
                last_ts = self._timebuffer[0]
                for idx, ts in enumerate(self._timebuffer):
                    if timestamp == ts:
                        self._buffer[idx].update({name: str(value)})
                        break
                    if last_ts < timestamp < ts:
                        self._buffer.insert(idx, {name: str(value)})
                        self._timebuffer.insert(idx, timestamp)
                        break
                    last_ts = ts

        # Write any rows in the buffer which exceed the size of buffer_target to the file.
        while len(self._buffer) >= buffer_target and len(self._buffer) > 0:
            row = self._buffer.popleft()
            row[self._header[0]] = self._timebuffer.popleft().strftime("%Y-%m-%d %H:%M:%S.%f")

            processed_row: list[str] = [""] * len(self._header)
            for idx, col in enumerate(self._header):
                if col in row:
                    v = self._latest_values[col] = row[col]
                    processed_row[idx] = str(v)
                else:
                    processed_row[idx] = str(self._latest_values.get(col, ""))

            log.debug(f"Writing line with index {processed_row[0]} to CSV file .")
            self._write_file(processed_row)

        # Close current file and create a new file with a different name if the size limit was exceeded.
        if size_limit_exceeded and buffer_target <= _len_buffer:
            log.info(f"CSV File size limit exceeded. Closing current file {self.filepath}.")
            self._file.close()
            self.filepath = self.filepath.with_name(f"{self.filepath.stem}_{datetime.now().strftime('%y%m%d%H%M')}.csv")

            self._open_file(exclusive_creation=True)

            if flush:
                self.write(flush=True)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        """Exit the context manager.

        :param exc_details: Execution details
        """
        if self._file is not None:
            self.write(flush=True)
            self._file.close()
