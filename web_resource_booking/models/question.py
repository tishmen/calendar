from odoo import fields, models


class ResourceBookingQuestion(models.Model):
    _name = "resource.booking.question"
    _description = "Resource Booking Question"
    _order = "sequence, id"

    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True)
    help = fields.Text(translate=True)
    type_id = fields.Many2one(
        comodel_name="resource.booking.type",
        string="Booking Type",
        required=True,
        ondelete="cascade",
        index=True,
    )
    field_type = fields.Selection(
        selection=[
            ("char", "Short text"),
            ("text", "Long text"),
            ("select", "Select"),
            ("boolean", "Yes / No"),
        ],
        required=True,
        default="char",
        # string redundant; label inferred from field name
    )
    required = fields.Boolean(default=False)
    option_ids = fields.One2many(
        comodel_name="resource.booking.question.option",
        inverse_name="question_id",
        string="Options",
        copy=True,
    )


class ResourceBookingQuestionOption(models.Model):
    _name = "resource.booking.question.option"
    _description = "Resource Booking Question Option"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True)
    question_id = fields.Many2one(
        comodel_name="resource.booking.question",
        string="Question",
        required=True,
        ondelete="cascade",
        index=True,
    )


class ResourceBookingAnswer(models.Model):
    _name = "resource.booking.answer"
    _description = "Resource Booking Answer"
    _order = "id"

    booking_id = fields.Many2one(
        comodel_name="resource.booking",
        string="Booking",
        required=True,
        ondelete="cascade",
        index=True,
    )
    question_id = fields.Many2one(
        comodel_name="resource.booking.question",
        string="Question",
        required=True,
        ondelete="cascade",
        index=True,
    )
    value = fields.Text(string="Answer")
