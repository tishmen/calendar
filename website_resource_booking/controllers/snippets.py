from odoo import http
from odoo.http import request


class WebsiteResourceBookingSnippets(http.Controller):
    """Controllers for website snippet integration.

    TODOs:
    - Provide dynamic snippet data (filters, records) once public pages exist.
    - Optionally expose a snippet filter to pick a default type or user.
    - Consider multi-website/company constraints.
    """

    # Placeholder endpoint if we need to feed dynamic content later.
    @http.route("/website_resource_booking/snippet/ping", type="json", auth="public", website=True)
    def ping(self):  # pragma: no cover - placeholder
        return {"status": "ok"}

