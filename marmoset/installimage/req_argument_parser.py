"""Simple module to get access to data from an http request"""


class ReqArgumentParser(object):
    """Simple class to get access to data from an http request"""

    def parse_args(self, req):
        """Method to parse arguments from a request"""
        return req.form
