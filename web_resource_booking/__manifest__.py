{
    "name": "Web Resource Booking",
    "summary": "Public portal view to schedule resource bookings and pick a user",
    "version": "19.0.1.0.0",
    "category": "Appointments",
    "website": "https://github.com/OCA/calendar",
    "author": "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["resource_booking", "portal"],
    "data": [
        "templates/public_portal.xml",
        "views/resource_booking_type_question_views.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            # Avoid loading resource_booking tours in frontend (breaks registry)
            ("remove", "resource_booking/static/src/js/booking_portal.esm.js"),
            ("remove", "resource_booking/static/src/js/tours/**/*"),
            # Our templates
            "web_resource_booking/static/src/xml/rbooking_form.xml",
        ],
        "web.assets_frontend_lazy": [
            "web_resource_booking/static/src/js/rbooking_form.esm.js",
            "web_resource_booking/static/src/js/rbooking_public_widget.esm.js",
        ],
        "web.assets_tests": [
            "web_resource_booking/static/src/js/tours/**/*",
        ],
    },
    "application": False,
    "installable": True,
    "demo": [
        "demo/questions_demo.xml",
        "demo/resource_booking_type_extra_demo.xml",
    ],
}
