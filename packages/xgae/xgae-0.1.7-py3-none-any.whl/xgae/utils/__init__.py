import logging

from .setup_env import setup_langfuse, setup_logging

setup_logging()
langfuse = setup_langfuse()

def handle_error(e: Exception) -> None:
    import traceback

    logging.error("An error occurred: %s", str(e))
    logging.error("Traceback details:\n%s", traceback.format_exc())
    raise (e) from e
