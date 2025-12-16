import logging
import sys
from pythonjsonlogger import jsonlogger


class DefaultFieldsFilter(logging.Filter):
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def filter(self, record: logging.LogRecord) -> bool:
        # Only set defaults if not already present.
        if not hasattr(record, "service"):
            record.service = self.service_name
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def configure_json_logging(service_name: str, level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(DefaultFieldsFilter(service_name))

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(service)s %(request_id)s"
    )
    handler.setFormatter(formatter)

    # Replace handlers to avoid duplicate logs
    root.handlers = [handler]
