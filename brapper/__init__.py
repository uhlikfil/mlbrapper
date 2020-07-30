import logging

from flask import Flask


def init_logging(logger: logging.Logger):
    fh = logging.FileHandler(f"logs/{__package__}")
    log_fmt = logging.Formatter("[%(asctime)s] %(name)s: %(levelname)s - %(message)s")
    fh.setFormatter(log_fmt)
    fh.setLevel(logging.DEBUG)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.info(f">>> SERVER STARTED <<<")


def create_app():
    server = Flask(__name__.split(".")[0])
    init_logging(server.logger)
    return server


app = create_app()

from brapper.server import endpoints
