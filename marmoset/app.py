from . import config, webserver

config = config.load()

app = webserver.app(config)

