"""initial file that handles marmoset"""
from marmoset import cli
from marmoset import config


def run(config_file=None):
    cfg = config.load_config(config_file)
    cli.parse(cfg)
