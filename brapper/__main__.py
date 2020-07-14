from brapper.server.api import server
import logging
from datetime import datetime


def init_logging():
    sanitized_datetime = str(datetime.now()).replace(":", "-").replace(".", "-")
    fh = logging.FileHandler(f"logs/{__package__}_{sanitized_datetime}")
    log_fmt = logging.Formatter("[%(asctime)s] %(name)s: %(levelname)s - %(message)s")
    fh.setFormatter(log_fmt)

    server.logger.addHandler(fh)
    server.logger.setLevel(logging.DEBUG)
    logging.info("Logging initialized!")


if __name__ == "__main__":
    init_logging()

    server.run(debug=True)
