import tomllib
import pathlib

import logging.config

LOGGING_CONFIG = pathlib.Path(__file__).parent / "Logger_config.toml"

with open(LOGGING_CONFIG, "rb") as f:
    data = tomllib.load(f)

default = data['handlers']['default']

print(default['class'])


logging.config.dictConfig(data)
