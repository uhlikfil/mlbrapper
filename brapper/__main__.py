from brapper.server.api import server
import logging


def init_logging():
    fh = logging.FileHandler(f"logs/{__package__}")
    log_fmt = logging.Formatter("[%(asctime)s] %(name)s: %(levelname)s - %(message)s")
    fh.setFormatter(log_fmt)

    server.logger.addHandler(fh)
    server.logger.setLevel(logging.DEBUG)
    server.logger.info(f">>> SERVER STARTED <<<")


if __name__ == "__main__":
    init_logging()

    server.run(debug=True)
