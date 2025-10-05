from datetime import datetime, timedelta, timezone

from odoo import api, fields, models


class ResourceBookingCleanup(models.Model):
    _inherit = "resource.booking"

    @api.model
    def cron_cleanup_prebookings(self):
        """Archive old pending bookings created via the web entry.

        Criteria:
        - state == 'pending' (no meeting yet)
        - active True
        - create_date older than configured threshold (default 48h)
        """
        icp = self.env["ir.config_parameter"].sudo()
        hours = float(icp.get_param("web_resource_booking.cleanup_hours", default="48") or 48)
        cutoff = fields.Datetime.to_string(datetime.utcnow() - timedelta(hours=hours))
        domain = [
            ("state", "=", "pending"),
            ("active", "=", True),
            ("create_date", "<", cutoff),
        ]
        old = self.sudo().search(domain, limit=500)
        if old:
            old.action_cancel()
        return True

