"""Simple module to get access to data from an http request."""


class ReqArgumentParser:
    """Simple class to get access to data from an http request."""

    def parse_args(self, req):
        """Parse arguments from a request."""
        return req.form
