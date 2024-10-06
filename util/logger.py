import json
from datetime import datetime, timedelta
from logging import config, getLogger


def setup_logger():
    with open("./logger.json", "r") as f:
        log_conf = json.load(f)
    log_conf["handlers"]["fileHandler"]["filename"] = "./logs/{}.log".format(
        datetime.utcnow().strftime("%Y%m%d%H%M%S")
    )
    config.dictConfig(log_conf)


def get_logger():
    return getLogger("__main__")
