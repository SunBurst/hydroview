import os
import logging.config

import yaml

from settings.settings import CONFIG_PATH

def setup_logging(
    #default_path='logging.yaml',
    default_path=(os.path.join(CONFIG_PATH, 'logging.yaml')),
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)