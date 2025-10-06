from datetime import timedelta

from odoo import api, fields, models


class ResourceBookingCleanup(models.Model):
    _inherit = "resource.booking"

    answer_ids = fields.One2many(
        comodel_name="resource.booking.answer",
        inverse_name="booking_id",
        string="Answers",
        help="Answers provided by the requester for configured questions.",
    )

    @api.model
    def cron_cleanup_prebookings(self):
        """Archive old pending bookings created via the web entry.

        Criteria:
        - state == 'pending' (no meeting yet)
        - active True
        - create_date older than configured threshold (default 48h)
        """
        icp = self.env["ir.config_parameter"].sudo()
        hours = float(
            icp.get_param("web_resource_booking.cleanup_hours", default="48") or 48
        )
        # If threshold is <= 0, consider all pending active bookings eligible.
        if hours <= 0:
            domain = [("state", "=", "pending"), ("active", "=", True)]
        else:
            # Use Odoo helpers and include boundary
            now = fields.Datetime.now()
            cutoff = fields.Datetime.to_string(now - timedelta(hours=hours))
            domain = [
                ("state", "=", "pending"),
                ("active", "=", True),
                ("create_date", "<=", cutoff),
            ]
        old = self.sudo().search(domain, limit=500)
        if old:
            old.action_cancel()
        return True
