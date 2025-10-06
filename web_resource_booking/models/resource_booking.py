from odoo import fields, models


class ResourceBooking(models.Model):
    _inherit = "resource.booking"

    answer_ids = fields.One2many(
        comodel_name="resource.booking.answer",
        inverse_name="booking_id",
        string="Answers",
        help="Answers provided by the requester for configured questions.",
    )
