import logging
import os

from langfuse import Langfuse

def setup_logging() -> None:
    import colorlog
    from dotenv import load_dotenv
    load_dotenv()

    env_log_level = os.getenv("LOG_LEVEL", "INFO")
    env_log_file = os.getenv("LOG_FILE", "log/xga.log")
    log_level = getattr(logging, env_log_level.upper(), logging.INFO)

    log_dir = os.path.dirname(env_log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    else:
        os.remove(env_log_file)

    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    }

    console_formatter = colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s %(white)s%(message)s',
        log_colors=log_colors,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_formatter = logging.Formatter(
        '%(asctime)s -%(levelname)-8s  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler(env_log_file, encoding='utf-8')
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.setLevel(log_level)

    logging.info(f"Logger is initialized, log_level={env_log_level}, log_file={env_log_file}")


def setup_langfuse() -> Langfuse:
    _langfuse = None
    env_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    env_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    env_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    if env_public_key and env_secret_key:
        _langfuse = Langfuse(tracing_enabled=True,
                            public_key=env_public_key,
                            secret_key=env_secret_key,
                            host=env_host)
        logging.info("Langfuse initialized Successfully by Key !")
    else:
        _langfuse = Langfuse(tracing_enabled=False)
        logging.warning("Not set key, Langfuse is disabled!")

    return _langfuse


if __name__ == "__main__":
        from xgae.utils import langfuse
        trace_id = langfuse.create_trace_id()
        logging.warning(f"trace_id={trace_id}")
