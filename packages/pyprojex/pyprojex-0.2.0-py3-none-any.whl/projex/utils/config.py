import json
import os

from .parser import parse
from .cutie import p


def get_config_name():
    data = parse()
    config = os.getenv("PROJEX_CONFIG_PATH", None)
    config = data.config if not config else config
    config = 'projex.json' if not config else config
    if not os.path.exists(config):
        p(
            f"There is no config file named {config}. Make sure you made a project here.",
            "fatal",
        )
    return "projex.json" if not config else config


def load():
    filename = get_config_name()
    with open(filename, "rb") as fp:
        return json.load(fp)


def save(new_config: dict):
    filename = get_config_name()
    with open(filename, "+w", encoding="utf-8") as fp:
        return json.dump(new_config, fp, indent=2)
