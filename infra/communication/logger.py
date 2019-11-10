import sys
import inspect
import logging

def logger():
    loggername=str(inspect.getouterframes(inspect.currentframe())[1][1]).split('/')[-1][:-3]
    logger = logging.getLogger(loggername)
    formatter = logging.Formatter(
        "[%(asctime)s] - [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)\n \033[F", datefmt="%d-%m-%Y %H:%M:%S")
    s_handler = logging.StreamHandler(sys.stdout)
    s_handler.flush = sys.stdout.flush
    s_handler.setLevel(logging.INFO)
    s_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    logger.setLevel(logging.INFO)
    return logger
