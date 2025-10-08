from odoo import api, fields, models


class ResourceBookingType(models.Model):
    _inherit = "resource.booking.type"

    question_ids = fields.One2many(
        comodel_name="resource.booking.question",
        inverse_name="type_id",
        string="Questions",
        help="Questions to ask requesters in the public booking form.",
    )

    slug = fields.Char(
        compute="_compute_slug",
        store=True,
        index=True,
        help="Computed slug for use in URLs and query parameters.",
    )

    note = fields.Text(
        help=(
            "Additional description for this booking type; "
            "can be shown on public forms."
        ),
    )
    image_1920 = fields.Image(
        string="Image",
        max_width=1920,
        max_height=1920,
        help="Image representing the booking type.",
    )

    @api.depends("name")
    def _compute_slug(self):
        IrHttp = self.env["ir.http"]
        for rec in self:
            try:
                # Use slugified name for readable URLs
                rec.slug = IrHttp._slugify(rec.name or "")
            except Exception:
                rec.slug = str(rec.id or "")
