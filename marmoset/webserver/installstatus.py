"""handle all web interaction with status updates from our installimage."""
from flask_restful import reqparse, Resource, abort
from flask import request
from marmoset.installstatus import InstallStatus
from marmoset import validation


class InstallStatusLatest(Resource):
    """latest status update for uuid."""

    def get(self, uuid):
        """Return the latest status based on provided UUID."""
        install_status = InstallStatus(uuid)
        latest_status = install_status.get_latest_status()
        if latest_status is None:
            return abort(404)
        return latest_status


class InstallStatusHistory(Resource):
    """status update history for uuid."""

    def get(self, uuid):
        """Return the history for a provided UUID."""
        install_status = InstallStatus(uuid)
        history = install_status.get_history()
        if not history:
            return abort(404)
        return history


class InstallStatusReport(Resource):
    """post new status update for uuid."""

    def post(self, uuid):
        """Create a new statusupdate for a UUID."""
        if not validation.is_uuid(uuid):
            return abort(404)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('status_code', type=int, required=True)
        parser.add_argument('step_description', type=str, required=True)
        parser.add_argument('current_step', type=int, required=True)
        parser.add_argument('total_steps', type=int, required=True)
        args = parser.parse_args(request)

        install = InstallStatus(uuid)
        install.insert_status(args.status_code, args.step_description,
                              args.current_step, args.total_steps)
        return


class InstallStatusStats(Resource):
    """stats related to the installimage job."""

    def get(self, uuid):
        """Return statistics for the performend installation based on provided UUID."""
        install_status = InstallStatus(uuid)
        stats = install_status.get_stats()
        if stats['start_date'] is None:
            return abort(404)
        return stats
