from marmoset import cli
from marmoset import config
from marmoset import validation


def run(config_file=None):
    cfg = config.load(config_file)
    cli.parse(cfg)
