# Copyright 2025 Milan Topuzov
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import re

from freezegun import freeze_time
from lxml.html import fromstring

from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.resource_booking.tests.common import create_test_data  # type: ignore


@freeze_time("2021-02-26 09:00:00", tick=True)
@tagged("post_install", "-at_install")
class WebResourceBookingPortalCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Reuse resource_booking test data (RBT, RBCs, Users, etc.)
        create_test_data(cls)

    def _get(self, url, data=None, timeout=10):
        resp = self.url_open(url, data=data, timeout=timeout)
        return resp

    def _get_xml(self, url, data=None, timeout=10):
        resp = self._get(url, data=data, timeout=timeout)
        return fromstring(resp.content)

    def _csrf_token(self, path="/rbooking"):
        resp = self._get(path)
        m = re.search(r'csrf_token:\s*"([^"]+)"', resp.text)
        self.assertTrue(m, "CSRF token not found on page")
        return m.group(1)

    def test_rbooking_index_page(self):
        page = self._get_xml("/rbooking")
        # Page title and mount div should be present
        self.assertTrue(page.cssselect("h2:contains('Book a Resource')"))
        mount = page.cssselect("#rbooking-app")
        self.assertTrue(mount, "rbooking mount node missing")
        # Hidden select must list available types
        type_options = page.cssselect("#rbooking-types-data option")
        self.assertGreaterEqual(len(type_options), 1)
        values = {opt.get("value") for opt in type_options}
        self.assertIn(str(self.rbt.id), values)

    def test_rbooking_users_json(self):
        # Should return users for the provided type
        resp = self._get(f"/rbooking/users?type_id={self.rbt.id}")
        self.assertEqual(resp.status_code, 200)
        payload = json.loads(resp.text)
        self.assertIn("users", payload)
        self.assertTrue(any(u["id"] == self.users[0].id for u in payload["users"]))

    def test_rbooking_start_creates_booking_and_redirects(self):
        # Post minimal data: type, user, name, email
        data = {
            "type_id": str(self.rbt.id),
            "user_id": str(self.users[0].id),
            "name": "Public Guest",
            "email": "guest@example.com",
        }
        data["csrf_token"] = self._csrf_token()
        resp = self._get("/rbooking/start", data=data)
        # After redirect, booking should exist for the partner email
        partner = self.env["res.partner"].search(
            [("email", "=ilike", data["email"])], limit=1
        )
        self.assertTrue(partner, "Partner not created for submitted email")
        booking = self.env["resource.booking"].search(
            [("partner_ids", "in", partner.id)], order="id desc", limit=1
        )
        self.assertTrue(booking, "Booking not created")
        self.assertEqual(booking.type_id, self.rbt)
        self.assertTrue(booking.combination_id, "Combination should be set")
        # Combination should include the selected user as a resource
        user_partner = self.users[0].partner_id
        self.assertIn(
            user_partner,
            booking.combination_id.resource_ids.user_id.partner_id,
        )
        # Redirect target should be the schedule view for the booking (tokenized)
        # If redirects were followed, ensure schedule page content is present
        content = resp.text or ""
        self.assertTrue(
            "/my/bookings/" in content
            or booking.get_portal_url(suffix="/schedule").split("?")[0] in content,
            "Expected redirect to schedule page",
        )

    def test_rbooking_users_invalid_type_returns_empty(self):
        resp = self._get("/rbooking/users?type_id=0")
        self.assertEqual(resp.status_code, 200)
        payload = json.loads(resp.text)
        self.assertEqual(payload.get("users"), [])

    def test_rbooking_start_missing_fields_redirects_back(self):
        # Missing email
        data = {
            "type_id": str(self.rbt.id),
            "user_id": str(self.users[0].id),
            "name": "Guest",
        }
        data["csrf_token"] = self._csrf_token()
        page = self._get_xml("/rbooking/start", data=data)
        # Back to the entry page
        self.assertTrue(
            page.cssselect("h2:contains('Book a Resource')")
            or page.cssselect("title:contains('Odoo')")
        )

    def test_rbooking_start_reuses_partner_by_normalized_email(self):
        # Create an existing partner with mixed-case email
        existing = self.env["res.partner"].create(
            {"name": "Guest", "email": "Guest+alias@Example.com"}
        )
        data = {
            "type_id": str(self.rbt.id),
            "user_id": str(self.users[0].id),
            "name": "Guest",
            "email": "GUEST+ALIAS@EXAMPLE.COM",
        }
        data["csrf_token"] = self._csrf_token()
        self._get("/rbooking/start", data=data)
        # Ensure no duplicate partner was created (reuse existing by normalized email)
        partners = self.env["res.partner"].search(
            [("email_normalized", "=", existing.email_normalized)]
        )
        self.assertEqual(len(partners), 1)
        booking = self.env["resource.booking"].search(
            [("partner_ids", "in", existing.id)], limit=1
        )
        self.assertTrue(booking)

    def test_rbooking_start_no_combo_redirects_back(self):
        # Create a user not present in any combination
        outsider = self.env["res.users"].create(
            {
                "login": "outsider",
                "name": "Outsider",
                "email": "outsider@example.com",
            }
        )
        data = {
            "type_id": str(self.rbt.id),
            "user_id": str(outsider.id),
            "name": "Guest",
            "email": "guest2@example.com",
        }
        data["csrf_token"] = self._csrf_token()
        page = self._get_xml("/rbooking/start", data=data)
        self.assertTrue(page.cssselect("h2:contains('Book a Resource')"))

    def test_cron_cleanup_cancels_old_pending(self):
        # Create a pending booking
        partner = self.env["res.partner"].create(
            {"name": "Old Guest", "email": "old@example.com"}
        )
        booking = self.env["resource.booking"].create(
            {
                "type_id": self.rbt.id,
                "partner_ids": [(6, 0, [partner.id])],
            }
        )
        # Set cleanup window to 0 hours so it's eligible immediately
        self.env["ir.config_parameter"].sudo().set_param(
            "web_resource_booking.cleanup_hours", "0"
        )
        # Run cron method
        self.env["resource.booking"].cron_cleanup_prebookings()
        booking.invalidate_model()
        self.assertFalse(booking.active)
        self.assertEqual(booking.state, "canceled")


@freeze_time("2021-02-26 09:00:00", tick=True)
@tagged("post_install", "-at_install", "tour")
class WebResourceBookingTourCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_data(cls)

    def test_rbooking_public_tour(self):
        # Minimal tour to assert the UI renders and interactions work
        self.start_tour("/rbooking", "web_resource_booking_public_tour")
