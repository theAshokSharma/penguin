import tomllib
import logging.config

with open("logger_config.toml", "rb") as f:
    data = tomllib.load(f)

default = data['handlers']['default']

print(default['class'])


logging.config.dictConfig(data)
