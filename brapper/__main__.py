from brapper.server.endpoints import server
import logging
import waitress


def init_logging():
    fh = logging.FileHandler(f"logs/{__package__}")
    log_fmt = logging.Formatter("[%(asctime)s] %(name)s: %(levelname)s - %(message)s")
    fh.setFormatter(log_fmt)
    fh.setLevel(logging.DEBUG)

    server.logger.setLevel(logging.DEBUG)
    server.logger.addHandler(fh)
    server.logger.info(f">>> SERVER STARTED <<<")


if __name__ == "__main__":
    init_logging()
    waitress.serve(server, host='0.0.0.0', port=5000)
    #server.run(debug=False)
