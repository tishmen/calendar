from odoo import http
from odoo.http import request
from odoo.tools.mail import email_normalize


class WebResourceBookingController(http.Controller):
    """Public entry to create a booking and redirect to the scheduler."""

    def _get_allowed_companies(self):
        website_company = request.website.company_id if getattr(request, "website", None) else request.env["res.company"]
        companies = request.env.companies
        return website_company if website_company in companies else companies

    def _visible_booking_types(self):
        Type = request.env["resource.booking.type"].sudo().with_context(active_test=True)
        domain = [("active", "=", True), ("company_id", "in", self._get_allowed_companies().ids)]
        types = Type.search(domain)
        # Keep only types that have at least one combination with a user resource
        return types.filtered(lambda t: any(res.user_id for res in t.mapped("combination_rel_ids.combination_id.resource_ids") if res.resource_type == "user"))

    def _staff_users_for_type(self, booking_type):
        resources = booking_type.mapped("combination_rel_ids.combination_id.resource_ids").filtered(lambda r: r.resource_type == "user" and r.user_id and r.active)
        users = resources.mapped("user_id").filtered("active")
        return users.sorted(lambda u: (u.name or "").lower())

    def _combos_for(self, booking_type, user):
        Comb = request.env["resource.booking.combination"].sudo()
        return Comb.search([
            ("type_rel_ids.type_id", "=", booking_type.id),
            ("resource_ids.user_id", "=", user.id),
            ("active", "=", True),
        ])

    @http.route(["/rbooking"], type="http", auth="public", website=True, sitemap=True)
    def rbooking_index(self, **kwargs):
        types = self._visible_booking_types()
        values = {"types": types}
        return request.render("web_resource_booking.rbooking_type_select", values)

    @http.route(["/rbooking/users"], type="http", auth="public", website=True, csrf=False)
    def rbooking_users(self, type_id=None, **kwargs):
        try:
            type_id = int(type_id or 0)
        except Exception:
            type_id = 0
        if not type_id:
            return request.make_json_response({"users": []})
        Type = request.env["resource.booking.type"].sudo()
        bt = Type.browse(type_id)
        if not bt or not bt.exists() or not bt.active or bt.company_id not in self._get_allowed_companies():
            return request.make_json_response({"users": []})
        users = self._staff_users_for_type(bt)
        payload = [{"id": u.id, "name": u.name or str(u.id)} for u in users]
        return request.make_json_response({"users": payload})

    @http.route(["/rbooking/start"], type="http", auth="public", website=True, methods=["POST"], csrf=True)
    def rbooking_start(self, **post):
        try:
            type_id = int(post.get("type_id"))
            user_id = int(post.get("user_id"))
        except Exception:
            return request.redirect("/rbooking")
        name = (post.get("name") or "").strip()
        email = (post.get("email") or "").strip()
        if not (name and email and type_id and user_id):
            # If fields are missing, just bounce back to the entry form
            return request.redirect("/rbooking")

        Type = request.env["resource.booking.type"].sudo()
        bt = Type.browse(type_id)
        user = request.env["res.users"].sudo().browse(user_id)
        if not (bt and bt.exists() and bt.active and user and user.exists() and user.active):
            return request.redirect("/rbooking")

        combos = self._combos_for(bt, user)
        if not combos:
            return request.redirect("/rbooking")

        Partner = request.env["res.partner"].sudo()
        normalized = email_normalize(email)
        domain = [("email_normalized", "=", normalized)] if normalized else [("email", "=ilike", email)]
        partner = Partner.search(domain, limit=1)
        if not partner:
            partner = Partner.create({"name": name, "email": email})

        Booking = request.env["resource.booking"].sudo()
        booking = Booking.create({
            "type_id": bt.id,
            "partner_ids": [(6, 0, [partner.id])],
            "combination_id": combos[0].id,
            "combination_auto_assign": False,
        })

        if request.env.user._is_public() and partner and partner.email:
            try:
                wiz = request.env["portal.wizard"].sudo().with_context(active_ids=[partner.id]).create({})
                for wu in wiz.user_ids:
                    wu.action_grant_access()
            except Exception:
                pass

        return request.redirect(booking.get_portal_url(suffix="/schedule"))
