from . import config, cli, validation

def run(config_file = None):
    cfg = config.load(config_file)
    cli.parse(cfg)

