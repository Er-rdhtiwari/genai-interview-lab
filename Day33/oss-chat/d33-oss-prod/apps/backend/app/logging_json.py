import logging
import sys
from pythonjsonlogger import jsonlogger


def configure_json_logging(service_name: str, level: str = "INFO") -> None:
    logger = logging.getLogger()
    logger.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(service)s %(request_id)s"
    )
    handler.setFormatter(formatter)

    # Replace handlers to avoid duplicate logs
    logger.handlers = [handler]

    # Add service field to all logs
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.service = service_name
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return record

    logging.setLogRecordFactory(record_factory)
import logging
import sys
from pythonjsonlogger import jsonlogger


def configure_json_logging(service_name: str, level: str = "INFO") -> None:
    logger = logging.getLogger()
    logger.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(service)s %(request_id)s"
    )
    handler.setFormatter(formatter)

    # Replace handlers to avoid duplicate logs
    logger.handlers = [handler]

    # Add service field to all logs
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.service = service_name
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return record

    logging.setLogRecordFactory(record_factory)
