import sys
from typing import List


class Logger:
    """
    Logger class for storing and flushing debug information.

    This class collects debug messages in memory and prints them
    all at once when flush() is called.
    """

    def __init__(self):
        """
        Initialize the logger with an empty message and outputs list.
        """
        self._messages: List[str] = []


    def log(self, message: str) -> None:
        """
        Store a debug message.

        Args:
            message: The debug message to store
        """
        self._messages.append(message)


    def flush(self) -> None:
        """
        Print all stored debug messages to the terminal and clear the buffer.
        """
        for message in self._messages:
            print(message, file=sys.stderr)
        self._messages.clear()


    def clear(self) -> None:
        """
        Clear all stored messages without printing them.
        """
        self._messages.clear()


    def __len__(self) -> int:
        """
        Return the number of stored messages.

        Returns:
            Number of messages in the buffer
        """
        return len(self._messages)
    

    def get_logs(self) -> List[str]:
        """
        Get a copy of the stored messages.

        Returns:
            List of stored messages
        """
        return self._messages.copy()


class OutputBuffer:
    """
    A custom output buffer to capture stdout writes. A wrapper around Logger.
    """

    def __init__(self):
        """
        Initialize the output buffer with a reference to a Logger.

        Args:
            logger: Logger instance to store output messages
        """
        self.logger = Logger()


    def write(self, message: str) -> None:
        """
        Write a message to the logger's output storage.

        Args:
            message: The message to write
        """
        self.logger.store(message)


    def flush(self) -> None:
        """
        Flush the output buffer.
        """
        for message in self.logger.get_logs():
            print(message)  # Print each message on a newline
