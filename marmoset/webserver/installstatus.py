from flask.ext.restful import reqparse, Resource, abort
from flask import request
from marmoset.installstatus import InstallStatus
from marmoset import validation


class InstallStatusLatest(Resource):
    """
    latest status update for uuid
    """

    def get(self, uuid):
        install_status = InstallStatus(uuid)
        install_status = install_status.get_latest_status()
        if install_status is None:
            return abort(404)
        return install_status


class InstallStatusHistory(Resource):
    """
    status update history for uuid
    """

    def get(self, uuid):
        install_status = InstallStatus(uuid)
        history = install_status.get_history()
        if len(history) == 0:
            return abort(404)
        return install_status


class InstallStatusReport(Resource):
    """
    post new status update for uuid
    """

    def post(self, uuid):
        if not validation.is_uuid(uuid):
            return abort(404)

        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str, required=True)
        args = parser.parse_args(request)

        if args.status is not None:
            install = InstallStatus(uuid)
            install.insert_status(args.status)
            return


class InstallStatusStats(Resource):
    """
    stats related to the installimage job
    """

    def get(self, uuid):
        install_status = InstallStatus(uuid)
        stats = install_status.get_stats()
        if stats['start_date'] is None:
            return abort(404)
        return stats