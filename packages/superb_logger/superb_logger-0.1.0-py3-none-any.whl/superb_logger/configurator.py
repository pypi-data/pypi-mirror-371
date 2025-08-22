"""Superb Logger Configurator Module.

This module provides a flexible and customizable logging configuration utility.
It allows setting up console and file handlers for multiple loggers with ease.

Classes:
    Configurator: Central class to configure and retrieve logger instances.
"""

from logging import FileHandler, Formatter, Logger, StreamHandler, getLogger

from .constants import DEFAULT_DATE_FORMAT, DEFAULT_FORMAT, ROOT_LOGGER_NAME
from .enums import Level


class Configurator:
    """Main class to configure and manage logger instances.

    Attributes:
        base_level: Default logging level for all loggers.
        loggers: Dictionary storing already configured logger instances.

    """

    base_level: int
    loggers: dict[str, Logger]

    def __init__(self, *, base_level: Level | int = Level.INFO) -> None:
        """Initialize the configurator with a default logging level.

        Args:
            base_level: Base logging level for all loggers (default is INFO).

        """
        self.loggers = {}
        self.base_level = base_level

    def get_logger(
        self,
        name: str,
        *,
        level: Level | None = None,
        to_console: bool = True,
        filepath: str | None = None,
    ) -> Logger:
        """Get or create a configured logger instance.

        Args:
            name: Name of the logger.
            level: Logging level for this specific logger.
            to_console: Whether to add a console handler.
            filepath: Path to a file for logging output.

        Returns:
            A configured Logger instance.

        """
        logger = self.loggers.get(name)
        if logger is None:
            logger = getLogger(name)

        logger.setLevel(level or self.base_level)
        if to_console:
            logger = self._set_console_handler(logger=logger)
        if filepath:
            logger = self._set_file_handler(logger=logger, filename=filepath)

        self.loggers[name] = logger
        return logger

    def get_root_logger(self) -> Logger:
        """Retrieve the root logger configured by this instance."""
        return self.get_logger(name=ROOT_LOGGER_NAME)

    def set_loggers(
        self,
        names: list[str],
        *,
        level: Level | None = None,
        to_console: bool = True,
    ) -> None:
        """Configure multiple loggers at once.

        Args:
            names: List of logger names to configure.
            level: Logging level for all these loggers.
            to_console: Whether to add a console handler.

        """
        for name in names:
            self.get_logger(name=name, level=level, to_console=to_console)

    @staticmethod
    def _default_formatter() -> Formatter:
        """Create and return a default log message formatter."""
        return Formatter(fmt=DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT)

    @staticmethod
    def _delete_handlers(
        logger: Logger,
        handler_class: FileHandler | StreamHandler,
    ) -> None:
        """Remove existing handlers of the specified class from the logger."""
        for handler in logger.handlers:
            if isinstance(handler, handler_class):
                logger.removeHandler(handler)

        return logger

    def _set_file_handler(self, logger: Logger, filename: str) -> Logger:
        """Add a file handler to the specified logger.

        Args:
            logger: Logger to which the handler will be added.
            filename: Path to the log file.

        Returns:
            Updated logger instance.

        """
        file_handler = FileHandler(filename=filename)
        file_handler.setFormatter(fmt=self._default_formatter())
        logger = self._delete_handlers(logger=logger, handler_class=FileHandler)
        logger.addHandler(hdlr=file_handler)
        return logger

    def _set_console_handler(self, logger: Logger) -> Logger:
        """Add a console handler to the specified logger.

        Args:
            logger: Logger to which the handler will be added.

        Returns:
            Updated logger instance.

        """
        console_handler = StreamHandler()
        console_handler.setFormatter(fmt=self._default_formatter())
        logger = self._delete_handlers(logger=logger, handler_class=StreamHandler)
        logger.addHandler(hdlr=console_handler)
        return logger
