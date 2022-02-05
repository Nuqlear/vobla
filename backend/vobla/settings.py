import configparser
import os


PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(PROJECT_PATH, "configuration")
ENV = os.environ.get("ENV", "dev")
CONFIG_PATH = os.path.join(CONFIG_DIR, "{}.ini".format(ENV))


config = configparser.SafeConfigParser(os.environ)
if os.path.exists(CONFIG_PATH):
    config.read(CONFIG_PATH)
