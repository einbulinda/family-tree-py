import logging
import logging.config
import os

def setup_logging():
    log_config_path = os.path.join(os.path.dirname(__file__),"../../logging.ini")
    if os.path.exists(log_config_path):
        logging.config.fileConfig(log_config_path, disable_existing_loggers=False)
    else:
        logging.basicConfig(level=logging.INFO)