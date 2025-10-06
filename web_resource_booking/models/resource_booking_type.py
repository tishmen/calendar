from odoo import fields, models


class ResourceBookingType(models.Model):
    _inherit = "resource.booking.type"

    question_ids = fields.One2many(
        comodel_name="resource.booking.question",
        inverse_name="type_id",
        string="Questions",
        help="Questions to ask requesters in the public booking form.",
    )
