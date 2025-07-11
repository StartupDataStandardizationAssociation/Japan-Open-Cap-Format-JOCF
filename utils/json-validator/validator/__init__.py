#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON Validator package initialization

Sets up default logging configuration with INFO level to prevent excessive output,
while ensuring DEBUG level logs are available for debugging purposes.
"""

import logging


# Set up default logging configuration
def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging configuration for the validator package

    Args:
        level (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Only configure our specific loggers, don't touch the root logger
    log_level = getattr(logging, level.upper())

    # Use a more specific logger name to avoid conflicts with other validator libraries
    json_validator_logger = logging.getLogger("json_validator")

    # Remove only our package's handlers if they exist
    for handler in json_validator_logger.handlers[:]:
        json_validator_logger.removeHandler(handler)

    # Create a console handler for our package
    if not json_validator_logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        json_validator_logger.addHandler(console_handler)

        # Prevent propagation to avoid duplicate messages if root logger also has handlers
        json_validator_logger.propagate = False

    # Set the level for our package logger
    json_validator_logger.setLevel(log_level)

    # Also set the level for our specific loggers
    for logger_name in [
        "json_validator.config_manager",
        "json_validator.schema_loader",
    ]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)


# Initialize logging with INFO level by default
setup_logging("INFO")

# Make setup_logging available for external configuration
__all__ = ["setup_logging"]
