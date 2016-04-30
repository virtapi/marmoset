from . import config, webserver

config = config.load_config()

app = webserver.app(config)
